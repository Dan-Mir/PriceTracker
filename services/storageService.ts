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

export const savePriceData = (data: {
  barcode?: string;
  name: string;
  supermarket: string;
  price: number;
}): Product[] => {
  const products = getProducts();
  const productId = data.barcode || `manual_${data.name.toLowerCase().trim().replace(/\s+/g, '-')}`;
  
  const existingProductIndex = products.findIndex(p => p.barcode === productId);
  
  const newPriceEntry: PriceEntry = {
    id: new Date().toISOString() + Math.random().toString(36).substring(2, 9),
    supermarket: data.supermarket,
    price: data.price,
    date: new Date().toISOString(),
  };

  if (existingProductIndex > -1) {
    products[existingProductIndex].priceHistory.push(newPriceEntry);
    if (data.barcode && data.name.length > products[existingProductIndex].name.length) {
      products[existingProductIndex].name = data.name;
    }
  } else {
    const newProduct: Product = {
      barcode: productId,
      name: data.name,
      priceHistory: [newPriceEntry],
    };
    products.push(newProduct);
  }

  saveProducts(products);
  return products;
};

export const deletePriceEntry = (productId: string, priceEntryId: string): Product[] => {
  let products = getProducts();
  const productIndex = products.findIndex(p => p.barcode === productId);

  if (productIndex > -1) {
    const updatedPriceHistory = products[productIndex].priceHistory.filter(
      entry => entry.id !== priceEntryId
    );

    if (updatedPriceHistory.length > 0) {
      products[productIndex].priceHistory = updatedPriceHistory;
    } else {
      products = products.filter(p => p.barcode !== productId);
    }
    
    saveProducts(products);
  }
  
  return products;
};