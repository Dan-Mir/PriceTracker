import axios from 'axios';
import { AlternativeProduct, Product, ShoppingListAnalysisResult } from '../types';
import { getAuthToken } from './authService';

const API_URL = '/api';

const apiClient = axios.create({
    baseURL: API_URL,
});

apiClient.interceptors.request.use(config => {
    const token = getAuthToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const getAlternativeSuggestions = async (productName: string): Promise<AlternativeProduct[]> => {
    try {
        const response = await apiClient.post('/gemini/suggestions', { productName });
        return response.data;
    } catch (error) {
        console.error("Error fetching suggestions from API", error);
        throw new Error("Failed to get suggestions from AI. Please try again.");
    }
};

export const analyzeShoppingList = async (shoppingList: string[], products: Product[]): Promise<ShoppingListAnalysisResult[]> => {
    try {
        const response = await apiClient.post('/gemini/analyze-list', { shoppingList, products });
        return response.data;
    } catch (error) {
        console.error("Error analyzing shopping list with API", error);
        throw new Error("Failed to get analysis from AI. Please try again.");
    }
};
