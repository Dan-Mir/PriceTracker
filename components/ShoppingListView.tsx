// FIX: Corrected the React import statement by removing the typo 'getE,'. This resolves all reported errors for this file.
import React, { useState, useEffect } from 'react';
import { Product, ShoppingListAnalysisResult } from '../types';
import { analyzeShoppingList } from '../services/geminiService';
import { getShoppingList, saveShoppingList } from '../services/storageService';
import { ShoppingCartIcon } from './icons/ShoppingCartIcon';
import { TrashIcon } from './icons/TrashIcon';

interface ShoppingListViewProps {
  products: Product[];
}

const ShoppingListView: React.FC<ShoppingListViewProps> = ({ products }) => {
  const [listItems, setListItems] = useState<{ text: string; id: string }[]>([]);
  const [newItemText, setNewItemText] = useState('');
  const [analysis, setAnalysis] = useState<ShoppingListAnalysisResult[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    setListItems(getShoppingList());
    const savedChecked = localStorage.getItem('shopping-list-checked');
    if (savedChecked) {
      setCheckedItems(new Set(JSON.parse(savedChecked)));
    }
  }, []);

  useEffect(() => {
    saveShoppingList(listItems);
  }, [listItems]);

  useEffect(() => {
    localStorage.setItem('shopping-list-checked', JSON.stringify(Array.from(checkedItems)));
  }, [checkedItems]);


  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (newItemText.trim()) {
      setListItems(prev => [...prev, { text: newItemText.trim(), id: Date.now().toString() }]);
      setNewItemText('');
    }
  };

  const handleRemoveItem = (idToRemove: string) => {
    setListItems(prev => prev.filter(item => item.id !== idToRemove));
    // Also remove from analysis if it exists
    if (analysis) {
        const correspondingItem = listItems.find(li => li.id === idToRemove);
        if (correspondingItem) {
            setAnalysis(prev => prev?.filter(res => res.itemName !== correspondingItem.text) ?? null);
        }
    }
  };

  const handleAnalyze = async () => {
    if (listItems.length === 0) {
        setError("Your shopping list is empty.");
        return;
    }
    setIsLoading(true);
    setError('');
    setAnalysis(null);
    try {
      const itemTexts = listItems.map(item => item.text);
      const result = await analyzeShoppingList(itemTexts, products);
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleChecked = (itemName: string) => {
    setCheckedItems(prev => {
        const newSet = new Set(prev);
        if (newSet.has(itemName)) {
            newSet.delete(itemName);
        } else {
            newSet.add(itemName);
        }
        return newSet;
    });
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 animate-fade-in grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <h2 className="text-3xl font-bold text-white mb-6">Create Your List</h2>
        <form onSubmit={handleAddItem} className="flex gap-2 mb-4">
          <input
            type="text"
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            placeholder="e.g., Milk, Bread, Soap..."
            className="flex-grow bg-gray-700 border border-gray-600 rounded-lg py-2 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary"
          />
          <button type="submit" className="bg-brand-primary hover:bg-brand-secondary text-white font-bold py-2 px-4 rounded-lg transition-colors">
            Add
          </button>
        </form>

        <div className="space-y-3 max-h-[40vh] overflow-y-auto pr-2 mb-4">
          {listItems.length > 0 ? (
            listItems.map(item => (
              <div key={item.id} className="flex justify-between items-center bg-gray-700/60 p-3 rounded-md">
                <span className={`text-white ${checkedItems.has(item.text) ? 'line-through text-gray-400' : ''}`}>{item.text}</span>
                <button onClick={() => handleRemoveItem(item.id)} className="text-gray-500 hover:text-red-400">
                  <TrashIcon className="w-5 h-5" />
                </button>
              </div>
            ))
          ) : (
            <p className="text-gray-400 text-center py-4">Your shopping list is empty.</p>
          )}
        </div>
        <button
            onClick={handleAnalyze}
            disabled={isLoading || listItems.length === 0}
            className="w-full bg-brand-secondary hover:bg-brand-secondary/80 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
            {isLoading ? 'Analyzing...' : 'Analyze with AI'}
        </button>
        {error && <p className="text-red-400 mt-2 text-center">{error}</p>}
      </div>
      <div>
        <h2 className="text-3xl font-bold text-white mb-6">AI Shopping Plan</h2>
        <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
            {isLoading && <p className="text-center text-gray-400">Assistant is thinking...</p>}
            {analysis ? (
                analysis.map(result => (
                    <div
                        key={result.itemName}
                        onClick={() => handleToggleChecked(result.itemName)}
                        className={`p-4 rounded-lg cursor-pointer transition-all ${checkedItems.has(result.itemName) ? 'bg-green-500/10' : 'bg-gray-700/60 hover:bg-gray-700'}`}
                    >
                        <div className="flex items-start">
                             <div className="flex items-center h-6 mt-1">
                                <input
                                    type="checkbox"
                                    checked={checkedItems.has(result.itemName)}
                                    readOnly
                                    className="form-checkbox h-5 w-5 text-brand-primary bg-gray-800 border-gray-600 rounded focus:ring-brand-secondary"
                                />
                            </div>
                            <div className="ml-3 text-sm">
                                <label className={`font-bold text-lg ${checkedItems.has(result.itemName) ? 'text-gray-400 line-through' : 'text-white'}`}>
                                    {result.itemName}
                                </label>
                                {result.status === 'FOUND' ? (
                                    <p className={`mt-1 ${checkedItems.has(result.itemName) ? 'text-gray-500' : 'text-gray-300'}`}>
                                        Buy <span className="font-semibold text-brand-primary">{result.matchedProductName}</span> at <span className="font-semibold">{result.bestSupermarket}</span> for <span className="font-semibold">${result.lowestPrice?.toFixed(2)}</span>
                                    </p>
                                ) : (
                                    <p className="mt-1 text-yellow-400">Not found in your price history.</p>
                                )}
                            </div>
                        </div>
                    </div>
                ))
            ) : (
                 !isLoading && (
                    <div className="flex flex-col items-center justify-center h-full text-center bg-gray-900/50 rounded-lg p-8">
                        <ShoppingCartIcon className="w-16 h-16 text-gray-600 mb-4" />
                        <p className="text-gray-400">Your optimized shopping plan will appear here after analysis.</p>
                    </div>
                 )
            )}
        </div>
      </div>
    </div>
  );
};

export default ShoppingListView;