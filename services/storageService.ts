import { Product } from '../types';

const PRODUCTS_STORAGE_KEY = 'priceTrackerProducts';

export const loadProducts = (): Product[] => {
  try {
    const serializedProducts = localStorage.getItem(PRODUCTS_STORAGE_KEY);
    if (serializedProducts === null) {
      return [];
    }
    return JSON.parse(serializedProducts);
  } catch (error) {
    console.error("Could not load products from local storage", error);
    return [];
  }
};

export const saveProducts = (products: Product[]): void => {
  try {
    const serializedProducts = JSON.stringify(products);
    localStorage.setItem(PRODUCTS_STORAGE_KEY, serializedProducts);
  } catch (error) {
    console.error("Could not save products to local storage", error);
  }
};
