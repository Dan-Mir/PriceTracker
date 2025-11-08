import React, { useState, useMemo } from 'react';
import { Product } from '../types';
import { SearchIcon } from './icons/SearchIcon';
import { TrashIcon } from './icons/TrashIcon';

interface ProductListProps {
  products: Product[];
  onProductSelect: (product: Product) => void;
  onDeleteProduct: (productId: string) => void;
}

const ProductList: React.FC<ProductListProps> = ({ products, onProductSelect, onDeleteProduct }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const handleDeleteClick = (productId: string) => {
    if (confirmDelete === productId) {
      onDeleteProduct(productId);
      setConfirmDelete(null);
    } else {
      setConfirmDelete(productId);
    }
  };

  const filteredAndSortedProducts = useMemo(() => {
    return products
      .filter(product =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [products, searchTerm]);

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 animate-fade-in">
      <h2 className="text-3xl font-bold text-white mb-6">All Tracked Products</h2>
      
      <div className="relative mb-6">
        <input
          type="text"
          placeholder="Search by product name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
        />
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      </div>

      <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
        {filteredAndSortedProducts.length > 0 ? (
          filteredAndSortedProducts.map(product => (
            <div key={product.barcode} className="flex items-center space-x-2">
              <button
                onClick={() => onProductSelect(product)}
                className="flex-grow text-left bg-gray-700/60 p-4 rounded-lg hover:bg-gray-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-brand-secondary"
              >
                <h3 className="font-semibold text-white">{product.name}</h3>
                <p className="text-sm font-mono text-gray-400">{product.barcode}</p>
              </button>
              <button
                onClick={() => handleDeleteClick(product.barcode)}
                className={`p-2 rounded-full transition-colors ${confirmDelete === product.barcode ? 'bg-red-500 text-white' : 'bg-gray-600 text-gray-400 hover:bg-red-500 hover:text-white'}`}
                aria-label={confirmDelete === product.barcode ? 'Confirm delete' : 'Delete product'}
              >
                <TrashIcon className="w-5 h-5" />
              </button>
            </div>
          ))
        ) : (
          <div className="text-center py-10">
            <p className="text-gray-400">
              {searchTerm ? 'No products match your search.' : 'You have not tracked any products yet.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductList;