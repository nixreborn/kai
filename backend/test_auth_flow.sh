#!/bin/bash
# Test authentication flow with CORS headers

echo "=== Testing Authentication Flow with CORS ==="
echo ""

# Check if backend is running
echo "1. Checking if backend is running on localhost:8000..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   ✗ Backend is not running. Please start with: cd backend && uv run uvicorn src.main:app --reload"
    exit 1
fi
echo "   ✓ Backend is running"
echo ""

# Test CORS preflight for registration endpoint
echo "2. Testing CORS preflight for /api/auth/register..."
PREFLIGHT=$(curl -s -X OPTIONS http://localhost:8000/api/auth/register \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -i)

if echo "$PREFLIGHT" | grep -q "access-control-allow-origin: http://localhost:3000"; then
    echo "   ✓ CORS preflight successful"
    echo "   ✓ Access-Control-Allow-Origin: http://localhost:3000"
else
    echo "   ✗ CORS preflight failed"
    echo "$PREFLIGHT"
    exit 1
fi

if echo "$PREFLIGHT" | grep -q "access-control-allow-credentials: true"; then
    echo "   ✓ Access-Control-Allow-Credentials: true"
else
    echo "   ✗ Missing credentials header"
fi
echo ""

# Test registration endpoint
echo "3. Testing registration endpoint..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"TestPassword123!\"}" \
  -i)

if echo "$REGISTER_RESPONSE" | grep -q "access-control-allow-origin"; then
    echo "   ✓ CORS headers present in registration response"
else
    echo "   ✗ CORS headers missing"
fi

if echo "$REGISTER_RESPONSE" | grep -q "HTTP/.*[23].."; then
    echo "   ✓ Registration endpoint responding (user may already exist)"
else
    echo "   Response:"
    echo "$REGISTER_RESPONSE" | head -20
fi
echo ""

echo "=== CORS Configuration Test Complete ==="
echo ""
echo "Next steps:"
echo "1. Start the backend: cd /home/nix/projects/kai/backend && uv run uvicorn src.main:app --reload"
echo "2. Start the frontend: cd /home/nix/projects/kai/frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo "4. Try registering a new account"
