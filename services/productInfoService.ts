const API_URL = 'https://world.openfoodfacts.org/api/v2/product/';

interface OpenFoodFactsResponse {
  code: string;
  product?: {
    product_name: string;
  };
  status: number;
  status_verbose: string;
}

export const fetchProductInfoByBarcode = async (barcode: string): Promise<{ name: string } | null> => {
  try {
    const response = await fetch(`${API_URL}${barcode}?fields=product_name`);
    if (!response.ok) {
      console.error(`API request failed with status: ${response.status}`);
      return null;
    }
    
    const data: OpenFoodFactsResponse = await response.json();
    
    if (data.product && data.product.product_name) {
      return { name: data.product.product_name };
    }
    
    console.warn(`Product not found for barcode: ${barcode}`, data);
    return null;

  } catch (error) {
    console.error("Error fetching product info from Open Food Facts API:", error);
    return null;
  }
};
