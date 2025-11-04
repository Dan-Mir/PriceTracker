import React from 'react';
import { BarcodeIcon } from './icons/BarcodeIcon';
import { HomeIcon } from './icons/HomeIcon';

interface HeaderProps {
  showHomeButton: boolean;
  onHomeClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ showHomeButton, onHomeClick }) => {
  return (
    <header className="bg-gray-800 shadow-md">
      <div className="container mx-auto px-4 py-4 md:px-6 md:py-5 flex items-center justify-between">
        <div className="flex items-center">
          <BarcodeIcon className="w-8 h-8 text-brand-primary" />
          <h1 className="ml-3 text-2xl md:text-3xl font-bold text-gray-100 tracking-tight">
            Supermarket Price Tracker
          </h1>
        </div>
        {showHomeButton && (
          <button 
            onClick={onHomeClick} 
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            aria-label="Back to home"
          >
            <HomeIcon className="w-5 h-5" />
            <span className="hidden sm:inline">Home</span>
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;