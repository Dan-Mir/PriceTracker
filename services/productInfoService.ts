import axios from 'axios';
import { getAuthToken } from './authService';

const API_URL = 'https://pricetracker-pwsp.onrender.com/api';

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


export const fetchProductInfoByBarcode = async (barcode: string): Promise<{ name: string } | null> => {
  try {
    const response = await apiClient.post('/barcode', { barcode });
    return response.data;
  } catch (error).
    console.error("Error fetching product info from API", error);
    return null;
  }
};
