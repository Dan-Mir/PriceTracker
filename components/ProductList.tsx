
import React, { useState } from 'react';
import { Product, PriceEntry } from '../types';
import GeminiSuggestions from './GeminiSuggestions';
import { ChevronDownIcon } from './icons/ChevronDownIcon';

interface ProductListProps {
  products: Product[];
}

const ProductItem: React.FC<{ product: Product }> = ({ product }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const sortedHistory = [...product.priceHistory].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  const latestEntry = sortedHistory[0];
  const lowestPrice = Math.min(...product.priceHistory.map(p => p.price));

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transition-all duration-300">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 text-left flex justify-between items-center hover:bg-gray-700/50 focus:outline-none"
      >
        <div>
          <h3 className="text-lg font-bold text-white">{product.name}</h3>
          <p className="text-sm text-gray-400">{product.barcode}</p>
          <div className="flex items-center space-x-4 mt-2 text-sm">
             <span className="text-green-400 font-semibold">
                Lowest: ${lowestPrice.toFixed(2)}
             </span>
             {latestEntry && (
                <span className="text-gray-300">
                    Latest: ${latestEntry.price.toFixed(2)} at {latestEntry.supermarket}
                </span>
             )}
          </div>
        </div>
        <ChevronDownIcon
          className={`w-6 h-6 text-gray-400 transform transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
        />
      </button>
      {isExpanded && (
        <div className="p-4 border-t border-gray-700 bg-gray-800/50">
          <h4 className="text-md font-semibold mb-3 text-gray-200">Price History</h4>
          <div className="space-y-2 mb-6 max-h-60 overflow-y-auto pr-2">
            {sortedHistory.map((entry: PriceEntry) => (
              <div key={entry.id} className="flex justify-between items-center bg-gray-700/50 p-3 rounded-md">
                <div>
                  <p className="font-semibold text-white">{entry.supermarket}</p>
                  <p className="text-xs text-gray-400">{new Date(entry.date).toLocaleDateString()}</p>
                </div>
                <p className="text-lg font-bold text-brand-primary">${entry.price.toFixed(2)}</p>
              </div>
            ))}
          </div>
           <GeminiSuggestions productName={product.name} />
        </div>
      )}
    </div>
  );
};

const ProductList: React.FC<ProductListProps> = ({ products }) => {
  return (
    <div className="space-y-4">
       <h2 className="text-2xl font-bold text-gray-200 border-b border-gray-700 pb-2">Tracked Products</h2>
      {products.map(product => (
        <ProductItem key={product.barcode} product={product} />
      ))}
    </div>
  );
};

export default ProductList;
