import React, { useState } from 'react';
import { login } from '../services/authService';
import { LockIcon } from './icons/LockIcon';
import { UserIcon } from './icons/UserIcon';

interface AuthViewProps {
  onLoginSuccess: () => void;
}

const AuthView: React.FC<AuthViewProps> = ({ onLoginSuccess }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Simulate API call
    setTimeout(() => {
      if (login(password)) {
        onLoginSuccess();
      } else {
        setError('Please enter a password.');
        setIsLoading(false);
      }
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white">
      <div className="w-full max-w-sm p-8 space-y-8 bg-gray-800 rounded-2xl shadow-lg animate-fade-in">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-brand-primary">PriceWise</h1>
          <p className="mt-2 text-gray-400">Your Personal Price Tracker</p>
        </div>
        <form className="space-y-6" onSubmit={handleLogin}>
          <div className="relative">
             <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <UserIcon className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 pl-10 pr-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="Username (any)"
              disabled
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
              placeholder="Password (any)"
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
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthView;
