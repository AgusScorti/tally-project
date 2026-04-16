// src/pages/LoginPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import api from '../api/client';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await api.post('/auth/login', {
          email,
          password,
        });
        const { access_token } = response.data;
        const userResponse = await api.get('/auth/me', {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        login(access_token, userResponse.data);
        navigate('/dashboard');
      } else {
        await api.post('/auth/register', {
          email,
          password,
          username,
          full_name: fullName,
        });
        setIsLogin(true);
        setEmail('');
        setPassword('');
        setFullName('');
        setUsername('');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-tally-light flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        {/* Logo / Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-tally-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <h1 className="text-2xl font-bold text-tally-text">Tally</h1>
          </div>
          <p className="text-tally-text/60 text-sm">
            {isLogin ? 'Track shared expenses' : 'Join Tally today'}
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-sm-tally p-8 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Full name
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all duration-200"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-tally-text mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all duration-200"
                    placeholder="johndoe"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-tally-text mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all duration-200"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-tally-text mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 border border-tally-border rounded-xl focus:outline-none focus:ring-2 focus:ring-tally-500 focus:border-transparent transition-all duration-200"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-tally-500 text-white py-2.5 rounded-xl font-medium hover:bg-tally-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {loading ? 'Loading...' : isLogin ? 'Sign in' : 'Create account'}
            </button>
          </form>
        </div>

        {/* Toggle */}
        <div className="text-center">
          <p className="text-tally-text/60 text-sm">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-tally-500 font-medium ml-1 hover:text-tally-600 transition-colors"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
