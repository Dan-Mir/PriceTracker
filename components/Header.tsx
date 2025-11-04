import React from 'react';
import { HomeIcon } from './icons/HomeIcon';
import { ShoppingCartIcon } from './icons/ShoppingCartIcon';
import { LogoutIcon } from './icons/LogoutIcon';

interface HeaderProps {
  currentView: string;
  onSetView: (view: 'home' | 'list') => void;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ currentView, onSetView, onLogout }) => {
  return (
    <header className="bg-gray-800 shadow-md p-4 flex justify-between items-center sticky top-0 z-40">
      <div className="flex items-center space-x-2">
        <h1 className="text-2xl font-bold text-brand-primary">PriceWise</h1>
      </div>
      <nav className="flex items-center space-x-2">
        <button
          onClick={() => onSetView('home')}
          className={`p-2 rounded-full transition-colors ${currentView === 'home' ? 'bg-brand-primary text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}`}
          aria-label="Home"
        >
          <HomeIcon className="w-6 h-6" />
        </button>
        <button
          onClick={() => onSetView('list')}
          className={`p-2 rounded-full transition-colors ${currentView === 'list' ? 'bg-brand-primary text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}`}
          aria-label="Shopping List"
        >
          <ShoppingCartIcon className="w-6 h-6" />
        </button>
         <button
          onClick={onLogout}
          className="p-2 rounded-full text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
          aria-label="Logout"
        >
          <LogoutIcon className="w-6 h-6" />
        </button>
      </nav>
    </header>
  );
};

export default Header;
