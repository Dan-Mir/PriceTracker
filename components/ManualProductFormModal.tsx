import React, { useState } from 'react';
import { XIcon } from './icons/XIcon';

interface ManualProductFormModalProps {
  onClose: () => void;
  onAddProduct: (entry: {
    name: string;
    supermarket: string;
    price: number;
  }) => void;
}

const ManualProductFormModal: React.FC<ManualProductFormModalProps> = ({ onClose, onAddProduct }) => {
  const [productName, setProductName] = useState('');
  const [supermarket, setSupermarket] = useState('');
  const [price, setPrice] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const priceNumber = parseFloat(price);
    if (!productName || !supermarket || !price || isNaN(priceNumber) || priceNumber <= 0) {
      setError('Please fill all fields correctly. Price must be a positive number.');
      return;
    }
    setError('');
    onAddProduct({ name: productName, supermarket, price: priceNumber });
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6 relative animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white"
          aria-label="Close modal"
        >
          <XIcon className="w-6 h-6" />
        </button>
        <h2 className="text-2xl font-bold mb-6 text-white">Add Manual Entry</h2>
        
        {error && <p className="bg-red-500/20 text-red-400 p-3 rounded-md mb-4">{error}</p>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="productName" className="block text-sm font-medium text-gray-300">Product Name</label>
            <input
              id="productName"
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              className="mt-1 w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="e.g., Organic Apples, Fresh Bread"
              autoFocus
            />
          </div>
          <div>
            <label htmlFor="supermarket" className="block text-sm font-medium text-gray-300">Supermarket</label>
            <input
              id="supermarket"
              type="text"
              value={supermarket}
              onChange={(e) => setSupermarket(e.target.value)}
              className="mt-1 w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="e.g., FreshMart, MegaGrocer"
            />
          </div>
          <div>
            <label htmlFor="price" className="block text-sm font-medium text-gray-300">Price</label>
            <input
              id="price"
              type="number"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="mt-1 w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="e.g., 3.49"
            />
          </div>
          <div className="pt-2">
            <button
              type="submit"
              className="w-full bg-brand-primary hover:bg-brand-secondary text-white font-bold py-3 px-4 rounded-lg transition-colors duration-300"
            >
              Save Price
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ManualProductFormModal;