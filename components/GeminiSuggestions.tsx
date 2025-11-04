
import React, { useState, useCallback } from 'react';
import { getAlternativeSuggestions } from '../services/geminiService';
import { AlternativeProduct } from '../types';

interface GeminiSuggestionsProps {
  productName: string;
}

const GeminiSuggestions: React.FC<GeminiSuggestionsProps> = ({ productName }) => {
  const [suggestions, setSuggestions] = useState<AlternativeProduct[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSuggestions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getAlternativeSuggestions(productName);
      setSuggestions(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [productName]);

  return (
    <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-gray-700">
      <h4 className="text-md font-semibold text-gray-200 mb-3">AI Product Alternatives</h4>
      {suggestions.length === 0 && !isLoading && (
        <button
          onClick={fetchSuggestions}
          disabled={isLoading}
          className="w-full bg-brand-secondary/80 hover:bg-brand-secondary text-white font-bold py-2 px-4 rounded-lg transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Thinking...' : 'Find Alternatives'}
        </button>
      )}

      {isLoading && <p className="text-center text-gray-400">Fetching suggestions...</p>}
      {error && <p className="text-center text-red-400">{error}</p>}
      
      {suggestions.length > 0 && (
        <div className="space-y-3">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="p-3 bg-gray-700/50 rounded-md">
              <p className="font-bold text-white">{suggestion.name}</p>
              <p className="text-sm text-gray-300">{suggestion.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GeminiSuggestions;
