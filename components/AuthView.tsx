import React, { useState } from 'react';
import { login, register } from '../services/authService';
import { LockIcon } from './icons/LockIcon';
import { UserIcon } from './icons/UserIcon';

interface AuthViewProps {
  onLoginSuccess: () => void;
}

const AuthView: React.FC<AuthViewProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (isRegister) {
      const success = await register(username, password);
      if (success) {
        setIsRegister(false);
        setError('Registration successful! Please log in.');
      } else {
        setError('Registration failed. Please try again.');
      }
    } else {
      const success = await login(username, password);
      if (success) {
        onLoginSuccess();
      } else {
        setError('Invalid username or password.');
      }
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white">
      <div className="w-full max-w-sm p-8 space-y-8 bg-gray-800 rounded-2xl shadow-lg animate-fade-in">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-brand-primary">PriceWise</h1>
          <p className="mt-2 text-gray-400">Your Personal Price Tracker</p>
        </div>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="relative">
             <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <UserIcon className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 pl-10 pr-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="Username"
            />
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <LockIcon className="w-5 h-5 text-gray-400" />
            </div>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 pl-10 pr-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="Password"
              autoFocus
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-brand-primary hover:bg-brand-secondary text-white font-bold py-3 px-4 rounded-lg transition-colors duration-300 disabled:opacity-50"
            >
              {isLoading ? 'Loading...' : (isRegister ? 'Register' : 'Sign In')}
            </button>
          </div>
        </form>
        <div className="text-center">
          <button onClick={() => setIsRegister(!isRegister)} className="text-sm text-gray-400 hover:underline">
            {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthView;
