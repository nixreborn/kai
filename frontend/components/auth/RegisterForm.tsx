/**
 * Registration form component
 */

'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AuthAPIError, isValidEmail, validatePassword } from '@/lib/api/auth';
import { Eye, EyeOff, Loader2, UserPlus, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

export function RegisterForm() {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.valid) {
        newErrors.password = passwordValidation.message || 'Invalid password';
      }
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    try {
      await register(formData.email, formData.password, formData.confirmPassword);
    } catch (error) {
      if (error instanceof AuthAPIError) {
        setErrors({ submit: error.message });
      } else if (error instanceof Error) {
        setErrors({ submit: error.message });
      } else {
        setErrors({ submit: 'An unexpected error occurred. Please try again.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Check password requirements
  const passwordRequirements = [
    { label: 'At least 8 characters', met: formData.password.length >= 8 },
    { label: 'One lowercase letter', met: /[a-z]/.test(formData.password) },
    { label: 'One uppercase letter', met: /[A-Z]/.test(formData.password) },
    { label: 'One number', met: /[0-9]/.test(formData.password) },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Email field */}
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Email address
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`w-full px-4 py-3 rounded-lg border ${
            errors.email
              ? 'border-red-300 dark:border-red-700 focus:ring-red-500 focus:border-red-500'
              : 'border-gray-300 dark:border-gray-600 focus:ring-aqua-500 focus:border-aqua-500'
          } bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 transition-colors`}
          placeholder="you@example.com"
          disabled={isLoading}
        />
        {errors.email && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.email}</p>
        )}
      </div>

      {/* Password field */}
      <div>
        <label
          htmlFor="password"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Password
        </label>
        <div className="relative">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="new-password"
            required
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            className={`w-full px-4 py-3 rounded-lg border ${
              errors.password
                ? 'border-red-300 dark:border-red-700 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 dark:border-gray-600 focus:ring-aqua-500 focus:border-aqua-500'
            } bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 transition-colors pr-12`}
            placeholder="Create a strong password"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        {/* Password requirements */}
        {formData.password && (
          <div className="mt-3 space-y-2">
            {passwordRequirements.map((req, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                <CheckCircle2
                  className={`w-4 h-4 ${
                    req.met
                      ? 'text-green-500 dark:text-green-400'
                      : 'text-gray-300 dark:text-gray-600'
                  }`}
                />
                <span
                  className={
                    req.met
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }
                >
                  {req.label}
                </span>
              </div>
            ))}
          </div>
        )}

        {errors.password && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.password}</p>
        )}
      </div>

      {/* Confirm password field */}
      <div>
        <label
          htmlFor="confirmPassword"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Confirm password
        </label>
        <div className="relative">
          <input
            id="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            autoComplete="new-password"
            required
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            className={`w-full px-4 py-3 rounded-lg border ${
              errors.confirmPassword
                ? 'border-red-300 dark:border-red-700 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 dark:border-gray-600 focus:ring-aqua-500 focus:border-aqua-500'
            } bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 transition-colors pr-12`}
            placeholder="Confirm your password"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
          >
            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
        {errors.confirmPassword && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.confirmPassword}</p>
        )}
      </div>

      {/* Submit error */}
      {errors.submit && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-600 dark:text-red-400">{errors.submit}</p>
        </div>
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-aqua-600 hover:bg-aqua-700 dark:bg-aqua-700 dark:hover:bg-aqua-600 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-aqua-500 focus:ring-offset-2"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Creating account...
          </>
        ) : (
          <>
            <UserPlus className="w-5 h-5" />
            Create account
          </>
        )}
      </button>

      {/* Sign in link */}
      <div className="text-center">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Already have an account?{' '}
          <Link
            href="/auth/login"
            className="text-aqua-600 dark:text-aqua-400 hover:text-aqua-700 dark:hover:text-aqua-300 font-medium transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
    </form>
  );
}
