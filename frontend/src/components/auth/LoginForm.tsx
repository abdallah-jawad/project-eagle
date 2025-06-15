'use client';

import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import './login.css';

const schema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().required('Password is required'),
});

type LoginFormData = yup.InferType<typeof schema>;

export default function LoginForm() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginFormData>({
    resolver: yupResolver(schema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      console.log('Starting login process...');
      const response = await authApi.login(data.email, data.password);
      console.log('Login response:', response);
      
      login(
        {
          id: response.client_id,
          email: data.email,
          name: data.email.split('@')[0],
        },
        response.access_token
      );
      
      console.log('Auth state updated, attempting navigation...');
      router.push('/dashboard');
    } catch (error: unknown) {
      console.error('Login error:', error);
      const errorMessage = 'Login failed. Please try again.';
      setError('root', {
        message: errorMessage,
      });
    }
  };

  return (
    <div className="login-container">
      <div className="login-gradient" />
      
      <div className="login-orb login-orb-1" />
      <div className="login-orb login-orb-2" />
      <div className="login-orb login-orb-3" />

      <div className="login-card">
        <div className="login-card-inner">
          <div className="login-header">
            <h2 className="login-title">
              Welcome!
            </h2>
            <p className="login-subtitle">Sign in to access your computer vision workspace</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit(onSubmit)}>
            <div className="login-form-group">
              <div className="relative">
                <input
                  {...register('email')}
                  type="email"
                  className="login-input"
                  placeholder="Email address"
                />
                {errors.email && (
                  <p className="login-error">{errors.email.message}</p>
                )}
              </div>

              <div className="relative">
                <input
                  {...register('password')}
                  type="password"
                  className="login-input"
                  placeholder="Password"
                />
                {errors.password && (
                  <p className="login-error">{errors.password.message}</p>
                )}
              </div>
            </div>

            {errors.root && (
              <div className="login-error-container">
                {errors.root.message}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="login-button"
            >
              <span className="login-button-text">
                {isSubmitting ? 'Authenticating...' : 'Sign in'}
              </span>
              <div className="login-button-gradient" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
} 