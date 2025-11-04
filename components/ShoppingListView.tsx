import React, { useState } from 'react';
import { analyzeShoppingList } from '../services/geminiService';
import { Product, ShoppingListAnalysisResult } from '../types';

interface ShoppingListViewProps {
  products: Product[];
}

const ShoppingListView: React.FC<ShoppingListViewProps> = ({ products }) => {
  const [listText, setListText] = useState('');
  const [analysisResult, setAnalysisResult] = useState<ShoppingListAnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    const shoppingList = listText.split('\n').map(item => item.trim()).filter(item => item);
    if (shoppingList.length === 0) {
      setError("Please enter at least one item in your shopping list.");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setAnalysisResult([]);
    
    try {
      const result = await analyzeShoppingList(shoppingList, products);
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const totalCost = analysisResult
    .filter(item => item.status === 'FOUND' && item.lowestPrice)
    .reduce((sum, item) => sum + (item.lowestPrice || 0), 0);
  
  const notFoundItems = analysisResult.filter(item => item.status === 'NOT_FOUND');

  return (
    <div className="p-4 sm:p-6 space-y-6 animate-fade-in">
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-3xl font-bold text-white mb-4">Shopping List Analyzer</h2>
        <p className="text-gray-400 mb-6">
          Enter your shopping list below (one item per line). The AI will cross-reference it with your tracked products to find the best prices.
        </p>

        <textarea
          value={listText}
          onChange={(e) => setListText(e.target.value)}
          rows={8}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
          placeholder="e.g.,&#10;Organic Milk&#10;Whole Wheat Bread&#10;Avocados"
        />
        <button
          onClick={handleAnalyze}
          disabled={isLoading || products.length === 0}
          className="mt-4 w-full bg-brand-primary hover:bg-brand-secondary text-white font-bold py-3 px-4 rounded-lg transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Analyzing...' : 'Analyze My List'}
        </button>
        {products.length === 0 && <p className="text-center text-yellow-400 mt-2 text-sm">You need to track some products first before using the analyzer.</p>}
        {error && <p className="text-center text-red-400 mt-4">{error}</p>}
      </div>

      {analysisResult.length > 0 && (
        <div className="bg-gray-800 rounded-lg shadow-lg p-6">
          <h3 className="text-2xl font-bold text-white mb-4">Analysis Results</h3>
          <div className="space-y-3">
            {analysisResult.map((item, index) => (
              <div key={index} className={`p-4 rounded-lg flex justify-between items-center ${item.status === 'FOUND' ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                <div>
                  <p className="font-semibold text-white">{item.itemName}</p>
                  {item.status === 'FOUND' ? (
                    <p className="text-sm text-gray-300">
                      Best price at <span className="font-bold text-green-300">{item.bestSupermarket}</span> for <span className="font-bold text-green-300">${item.lowestPrice?.toFixed(2)}</span>
                       <span className="text-gray-400 text-xs"> (matched: {item.matchedProductName})</span>
                    </p>
                  ) : (
                    <p className="text-sm text-red-300">Not found in your tracked products.</p>
                  )}
                </div>
                {item.status === 'FOUND' && <p className="text-xl font-bold text-white">${item.lowestPrice?.toFixed(2)}</p>}
              </div>
            ))}
          </div>
          <div className="mt-6 border-t border-gray-700 pt-4 text-right">
              <p className="text-gray-300">Estimated Total Cost:</p>
              <p className="text-3xl font-bold text-brand-primary">${totalCost.toFixed(2)}</p>
          </div>
           {notFoundItems.length > 0 && (
            <div className="mt-4 border-t border-gray-700 pt-4">
              <h4 className="font-semibold text-yellow-300">Items Not Found:</h4>
              <ul className="list-disc list-inside text-gray-400">
                {notFoundItems.map(item => <li key={item.itemName}>{item.itemName}</li>)}
              </ul>
            </div>
           )}
        </div>
      )}
    </div>
  );
};

export default ShoppingListView;
