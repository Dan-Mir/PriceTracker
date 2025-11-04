import React from 'react';
import { Product, PriceEntry } from '../types';
import GeminiSuggestions from './GeminiSuggestions';

interface ProductDetailViewProps {
  product: Product;
  onClose: () => void;
}

const ProductDetailView: React.FC<ProductDetailViewProps> = ({ product }) => {
  const sortedHistory = [...product.priceHistory].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  const latestEntry = sortedHistory[0];
  const lowestPriceEntry = product.priceHistory.reduce((min, p) => p.price < min.price ? p : min, product.priceHistory[0]);
  const highestPriceEntry = product.priceHistory.reduce((max, p) => p.price > max.price ? p : max, product.priceHistory[0]);

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 animate-fade-in">
      <h2 className="text-3xl font-bold text-white mb-2">{product.name}</h2>
      <p className="font-mono text-gray-400 mb-6">{product.barcode}</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 text-center">
        <div className="bg-green-500/10 p-4 rounded-lg">
          <p className="text-sm text-green-300">Lowest Price</p>
          <p className="text-2xl font-bold text-white">${lowestPriceEntry.price.toFixed(2)}</p>
          <p className="text-xs text-gray-400">at {lowestPriceEntry.supermarket}</p>
        </div>
        <div className="bg-blue-500/10 p-4 rounded-lg">
          <p className="text-sm text-blue-300">Latest Price</p>
          <p className="text-2xl font-bold text-white">${latestEntry.price.toFixed(2)}</p>
           <p className="text-xs text-gray-400">at {latestEntry.supermarket}</p>
        </div>
        <div className="bg-red-500/10 p-4 rounded-lg">
          <p className="text-sm text-red-300">Highest Price</p>
          <p className="text-2xl font-bold text-white">${highestPriceEntry.price.toFixed(2)}</p>
           <p className="text-xs text-gray-400">at {highestPriceEntry.supermarket}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-semibold mb-4 text-gray-200">Price History</h3>
          <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
            {sortedHistory.map((entry: PriceEntry) => (
              <div key={entry.id} className="flex justify-between items-center bg-gray-700/60 p-3 rounded-md">
                <div>
                  <p className="font-semibold text-white">{entry.supermarket}</p>
                  <p className="text-xs text-gray-400">{new Date(entry.date).toLocaleDateString()}</p>
                </div>
                <p className="text-lg font-bold text-brand-primary">${entry.price.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>
        <div>
           <GeminiSuggestions productName={product.name} />
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;