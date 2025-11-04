import { Product } from '../types';

const PRODUCTS_STORAGE_KEY = 'supermarket-price-tracker-products';
const SHOPPING_LIST_STORAGE_KEY = 'supermarket-price-tracker-shopping-list';

// Product Functions
export const getProducts = (): Product[] => {
  try {
    const productsJson = localStorage.getItem(PRODUCTS_STORAGE_KEY);
    return productsJson ? (JSON.parse(productsJson) as Product[]) : [];
  } catch (error) {
    console.error("Error reading products from localStorage", error);
    return [];
  }
};

export const saveProducts = (products: Product[]): void => {
  try {
    localStorage.setItem(PRODUCTS_STORAGE_KEY, JSON.stringify(products));
  } catch (error) {
    console.error("Error saving products to localStorage", error);
  }
};

// Shopping List Functions
export const getShoppingList = (): { text: string; id: string }[] => {
    try {
        const listJson = localStorage.getItem(SHOPPING_LIST_STORAGE_KEY);
        return listJson ? JSON.parse(listJson) : [];
    } catch (error) {
        console.error("Error reading shopping list from localStorage", error);
        return [];
    }
};

export const saveShoppingList = (list: { text: string; id: string }[]): void => {
    try {
        localStorage.setItem(SHOPPING_LIST_STORAGE_KEY, JSON.stringify(list));
    } catch (error) {
        console.error("Error saving shopping list to localStorage", error);
    }
};
