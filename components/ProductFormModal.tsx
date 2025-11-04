import React, { useState } from 'react';
import { XIcon } from './icons/XIcon';

interface ProductFormModalProps {
  onClose: () => void;
  onAddProduct: (entry: {
    supermarket: string;
    price: number;
  }) => void;
  barcode: string;
  productName: string;
}

const ProductFormModal: React.FC<ProductFormModalProps> = ({ onClose, onAddProduct, barcode, productName }) => {
  const [supermarket, setSupermarket] = useState('');
  const [price, setPrice] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const priceNumber = parseFloat(price);
    if (!supermarket || !price || isNaN(priceNumber) || priceNumber <= 0) {
      setError('Please fill all fields correctly. Price must be a positive number.');
      return;
    }
    setError('');
    onAddProduct({ supermarket, price: priceNumber });
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
        <h2 className="text-2xl font-bold mb-6 text-white">Add New Price Entry</h2>
        
        <div className="mb-4 p-4 bg-gray-900/50 rounded-lg border border-gray-700">
            <p className="text-sm text-gray-400">Product Name</p>
            <p className="text-lg font-semibold text-white">{productName}</p>
            <p className="text-sm text-gray-400 mt-2">Barcode</p>
            <p className="font-mono text-gray-300">{barcode}</p>
        </div>

        {error && <p className="bg-red-500/20 text-red-400 p-3 rounded-md mb-4">{error}</p>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="supermarket" className="block text-sm font-medium text-gray-300">Supermarket</label>
            <input
              id="supermarket"
              type="text"
              value={supermarket}
              onChange={(e) => setSupermarket(e.target.value)}
              className="mt-1 w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
              placeholder="e.g., FreshMart, MegaGrocer"
              autoFocus
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

export default ProductFormModal;