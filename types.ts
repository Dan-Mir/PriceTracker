
export interface PriceEntry {
  id: string;
  supermarket: string;
  price: number;
  date: string;
}

export interface Product {
  barcode: string;
  name: string;
  priceHistory: PriceEntry[];
}

export interface AlternativeProduct {
  name: string;
  reason: string;
}
