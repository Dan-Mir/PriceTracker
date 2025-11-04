export interface PriceEntry {
  id: string;
  supermarket: string;
  price: number;
  date: string; // ISO date string
}

export interface Product {
  barcode: string; // Also serves as ID
  name: string;
  priceHistory: PriceEntry[];
}

export interface AlternativeProduct {
  name: string;
  reason: string;
}

export interface ShoppingListAnalysisResult {
  itemName: string;
  status: 'FOUND' | 'NOT_FOUND';
  matchedProductName?: string;
  bestSupermarket?: string;
  lowestPrice?: number;
}
