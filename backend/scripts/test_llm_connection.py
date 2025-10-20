"""Test LLM service connectivity and functionality.

This script tests the LLM endpoint to verify:
1. Connectivity to the LLM service
2. Model availability
3. Chat completion endpoint
4. Response latency
5. Error handling (timeout, network errors)
"""

import asyncio
import time
from typing import Any

from openai import AsyncOpenAI, APIError, APITimeoutError, APIConnectionError

# LLM endpoint configuration
LLM_BASE_URL = "http://192.168.1.7:8000/v1"
LLM_API_KEY = "optional-api-key"
DEFAULT_TIMEOUT = 30.0


class LLMConnectionTester:
    """Test LLM service connectivity and functionality."""

    def __init__(self, base_url: str, api_key: str, timeout: float = DEFAULT_TIMEOUT):
        """Initialize the tester with LLM configuration."""
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )
        self.results: dict[str, Any] = {}

    async def test_connectivity(self) -> bool:
        """Test basic connectivity to the LLM service."""
        print(f"\n[TEST 1] Testing connectivity to {self.base_url}...")
        try:
            start_time = time.time()
            # Try to list models as a connectivity check
            models = await self.client.models.list()
            elapsed = time.time() - start_time

            print(f"  ✓ Connected successfully in {elapsed:.2f}s")
            self.results["connectivity"] = {
                "status": "success",
                "latency": elapsed,
                "models_count": len(models.data) if hasattr(models, 'data') else 0,
            }
            return True
        except APIConnectionError as e:
            print(f"  ✗ Connection failed: {e}")
            self.results["connectivity"] = {"status": "failed", "error": str(e)}
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            self.results["connectivity"] = {"status": "error", "error": str(e)}
            return False

    async def test_model_availability(self) -> list[str]:
        """Test and list available models."""
        print(f"\n[TEST 2] Checking model availability...")
        try:
            models_response = await self.client.models.list()
            models = []

            if hasattr(models_response, 'data'):
                models = [model.id for model in models_response.data]
                print(f"  ✓ Found {len(models)} available models:")
                for model in models:
                    print(f"    - {model}")
            else:
                print("  ! No models data returned, service may not support /models endpoint")
                models = ["default"]  # Fallback

            self.results["model_availability"] = {
                "status": "success",
                "models": models,
            }
            return models
        except Exception as e:
            print(f"  ✗ Failed to list models: {e}")
            print(f"  → Using fallback model: 'default'")
            self.results["model_availability"] = {
                "status": "partial",
                "error": str(e),
                "models": ["default"],
            }
            return ["default"]

    async def test_chat_completion(self, model: str = "default") -> bool:
        """Test chat completion endpoint."""
        print(f"\n[TEST 3] Testing chat completion with model '{model}'...")
        try:
            start_time = time.time()

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, this is a test' in exactly those words."}
                ],
                max_tokens=50,
                temperature=0.7,
            )

            elapsed = time.time() - start_time

            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                print(f"  ✓ Chat completion successful in {elapsed:.2f}s")
                print(f"    Response: {content[:100]}...")
                print(f"    Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")

                self.results["chat_completion"] = {
                    "status": "success",
                    "latency": elapsed,
                    "model": model,
                    "response_length": len(content) if content else 0,
                    "tokens": response.usage.total_tokens if response.usage else None,
                }
                return True
            else:
                print(f"  ✗ No response content received")
                self.results["chat_completion"] = {
                    "status": "failed",
                    "error": "No response content",
                }
                return False

        except APITimeoutError as e:
            print(f"  ✗ Request timed out after {self.timeout}s: {e}")
            self.results["chat_completion"] = {
                "status": "timeout",
                "error": str(e),
            }
            return False
        except APIError as e:
            print(f"  ✗ API error: {e}")
            self.results["chat_completion"] = {
                "status": "api_error",
                "error": str(e),
            }
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            self.results["chat_completion"] = {
                "status": "error",
                "error": str(e),
            }
            return False

    async def test_latency(self, model: str = "default", iterations: int = 3) -> dict[str, float]:
        """Measure response latency over multiple requests."""
        print(f"\n[TEST 4] Measuring latency over {iterations} requests...")
        latencies = []

        for i in range(iterations):
            try:
                start_time = time.time()
                await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": f"Respond with just the number {i+1}"}
                    ],
                    max_tokens=10,
                )
                elapsed = time.time() - start_time
                latencies.append(elapsed)
                print(f"  Request {i+1}: {elapsed:.2f}s")
            except Exception as e:
                print(f"  Request {i+1} failed: {e}")

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)

            print(f"  ✓ Latency statistics:")
            print(f"    Average: {avg_latency:.2f}s")
            print(f"    Min: {min_latency:.2f}s")
            print(f"    Max: {max_latency:.2f}s")

            self.results["latency"] = {
                "status": "success",
                "average": avg_latency,
                "min": min_latency,
                "max": max_latency,
                "samples": len(latencies),
            }
            return {
                "avg": avg_latency,
                "min": min_latency,
                "max": max_latency,
            }
        else:
            print(f"  ✗ All latency tests failed")
            self.results["latency"] = {
                "status": "failed",
                "error": "All requests failed",
            }
            return {}

    async def test_error_handling(self) -> None:
        """Test error handling scenarios."""
        print(f"\n[TEST 5] Testing error handling...")

        # Test 1: Invalid model
        print("  Testing invalid model...")
        try:
            await self.client.chat.completions.create(
                model="nonexistent-model-xyz",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            print("    ! No error raised for invalid model (may be expected)")
            self.results["error_handling_invalid_model"] = {"status": "no_error"}
        except Exception as e:
            print(f"    ✓ Correctly raised error: {type(e).__name__}")
            self.results["error_handling_invalid_model"] = {
                "status": "error_raised",
                "error_type": type(e).__name__,
            }

        # Test 2: Very short timeout
        print("  Testing timeout handling...")
        try:
            short_timeout_client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=0.001,  # 1ms - should timeout
            )
            await short_timeout_client.chat.completions.create(
                model="default",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            print("    ! Request completed despite very short timeout")
            self.results["error_handling_timeout"] = {"status": "no_timeout"}
        except APITimeoutError:
            print("    ✓ Correctly raised timeout error")
            self.results["error_handling_timeout"] = {
                "status": "timeout_raised",
                "error_type": "APITimeoutError",
            }
        except Exception as e:
            print(f"    ✓ Raised error: {type(e).__name__}")
            self.results["error_handling_timeout"] = {
                "status": "error_raised",
                "error_type": type(e).__name__,
            }

    async def test_streaming(self, model: str = "default") -> bool:
        """Test streaming response capability."""
        print(f"\n[TEST 6] Testing streaming responses...")
        try:
            start_time = time.time()
            chunks_received = 0

            stream = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Count from 1 to 5"}
                ],
                max_tokens=50,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    chunks_received += 1

            elapsed = time.time() - start_time

            print(f"  ✓ Streaming successful in {elapsed:.2f}s")
            print(f"    Chunks received: {chunks_received}")

            self.results["streaming"] = {
                "status": "success",
                "chunks": chunks_received,
                "latency": elapsed,
            }
            return True
        except Exception as e:
            print(f"  ✗ Streaming failed: {e}")
            self.results["streaming"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total_tests = len(self.results)
        passed_tests = sum(
            1 for r in self.results.values()
            if isinstance(r, dict) and r.get("status") in ["success", "partial", "no_error", "error_raised", "timeout_raised"]
        )

        print(f"\nTests completed: {total_tests}")
        print(f"Tests passed: {passed_tests}")
        print(f"Tests failed: {total_tests - passed_tests}")

        print(f"\nLLM Service: {self.base_url}")

        if self.results.get("connectivity", {}).get("status") == "success":
            print("Status: ✓ ONLINE")

            if "latency" in self.results and self.results["latency"].get("status") == "success":
                avg_latency = self.results["latency"]["average"]
                print(f"Average Latency: {avg_latency:.2f}s")

            if "model_availability" in self.results:
                models = self.results["model_availability"].get("models", [])
                print(f"Available Models: {', '.join(models)}")
        else:
            print("Status: ✗ OFFLINE")

        print("\nRecommendations:")

        if self.results.get("connectivity", {}).get("status") != "success":
            print("  - Verify LLM service is running at", self.base_url)
            print("  - Check network connectivity and firewall rules")
        elif self.results.get("chat_completion", {}).get("status") != "success":
            print("  - Chat completion failed - check model availability")
            print("  - Verify API compatibility (OpenAI format)")
        else:
            latency = self.results.get("latency", {})
            if latency.get("status") == "success":
                avg = latency.get("average", 0)
                if avg > 5:
                    print(f"  - High average latency ({avg:.2f}s) - consider performance tuning")
                elif avg > 10:
                    print(f"  - Very high latency ({avg:.2f}s) - investigate server performance")
                else:
                    print("  ✓ LLM service is performing well")

            if not self.results.get("streaming", {}).get("status") == "success":
                print("  - Streaming not supported or failed - some features may be limited")

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all LLM connection tests."""
        print("="*60)
        print("LLM SERVICE CONNECTION TEST")
        print("="*60)
        print(f"Endpoint: {self.base_url}")
        print(f"Timeout: {self.timeout}s")

        # Test 1: Connectivity
        if not await self.test_connectivity():
            print("\n✗ Connectivity test failed. Skipping remaining tests.")
            self.print_summary()
            return self.results

        # Test 2: Model availability
        models = await self.test_model_availability()
        test_model = models[0] if models else "default"

        # Test 3: Chat completion
        await self.test_chat_completion(test_model)

        # Test 4: Latency
        await self.test_latency(test_model)

        # Test 5: Error handling
        await self.test_error_handling()

        # Test 6: Streaming
        await self.test_streaming(test_model)

        # Print summary
        self.print_summary()

        return self.results


async def main():
    """Main test runner."""
    tester = LLMConnectionTester(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        timeout=DEFAULT_TIMEOUT,
    )

    results = await tester.run_all_tests()

    # Exit with appropriate code
    connectivity_ok = results.get("connectivity", {}).get("status") == "success"
    chat_ok = results.get("chat_completion", {}).get("status") == "success"

    if connectivity_ok and chat_ok:
        print("\n✓ All critical tests passed")
        return 0
    else:
        print("\n✗ Critical tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
