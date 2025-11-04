import { Product, PriceEntry } from '../types';

const PRODUCTS_KEY = 'supermarketPriceTrackerProducts';

export const getProducts = (): Product[] => {
  try {
    const productsJson = localStorage.getItem(PRODUCTS_KEY);
    return productsJson ? JSON.parse(productsJson) : [];
  } catch (error) {
    console.error("Failed to parse products from localStorage", error);
    return [];
  }
};

export const saveProducts = (products: Product[]): void => {
  try {
    localStorage.setItem(PRODUCTS_KEY, JSON.stringify(products));
  } catch (error) {
    console.error("Failed to save products to localStorage", error);
  }
};

export const findProductByBarcode = (barcode: string): Product | undefined => {
  const products = getProducts();
  return products.find(p => p.barcode === barcode);
};

export const addProductEntry = (entry: {
  barcode: string;
  name: string;
  supermarket: string;
  price: number;
}): Product[] => {
  const products = getProducts();
  const existingProductIndex = products.findIndex(p => p.barcode === entry.barcode);
  
  const newPriceEntry: PriceEntry = {
    id: new Date().toISOString(),
    supermarket: entry.supermarket,
    price: entry.price,
    date: new Date().toISOString(),
  };

  if (existingProductIndex > -1) {
    products[existingProductIndex].priceHistory.push(newPriceEntry);
    // If the new entry provides a more detailed name, update it.
    if (entry.name.length > products[existingProductIndex].name.length) {
      products[existingProductIndex].name = entry.name;
    }
  } else {
    const newProduct: Product = {
      barcode: entry.barcode,
      name: entry.name,
      priceHistory: [newPriceEntry],
    };
    products.push(newProduct);
  }

  saveProducts(products);
  return products;
};