import axios from 'axios';
import { Product } from '../types';
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

export const loadProducts = async (): Promise<Product[]> => {
    try {
        const response = await apiClient.get('/products');
        return response.data;
    } catch (error) {
        console.error("Could not load products from API", error);
        return [];
    }
};

export const addOrUpdateProduct = async (productData: {
    barcode: string;
    name: string;
    priceEntry: { supermarket: string; price: number, date: string, id: string };
}): Promise<Product[]> => {
    try {
        const response = await apiClient.post('/products', productData);
        return response.data;
    } catch (error) {
        console.error("Could not save product to API", error);
        throw error;
    }
};

export const deletePriceEntry = async (productId: string, entryId: string): Promise<Product[]> => {
    try {
        const response = await apiClient.delete(`/products/${productId}/entries/${entryId}`);
        return response.data;
    } catch (error) {
        console.error("Could not delete price entry from API", error);
        throw error;
    }
}
