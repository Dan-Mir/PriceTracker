import React, { useState, useEffect, useCallback } from 'react';
import { Product, PriceEntry } from './types';
import { loadProducts, addOrUpdateProduct as apiAddOrUpdateProduct, deletePriceEntry as apiDeletePriceEntry } from './services/storageService';
import { fetchProductInfoByBarcode } from './services/productInfoService';
import ProductList from './components/ProductList';
import ProductDetailView from './components/ProductDetailView';
import BarcodeScannerModal from './components/BarcodeScannerModal';
import ProductFormModal from './components/ProductFormModal';
import ManualProductFormModal from './components/ManualProductFormModal';
import Header from './components/Header';
import ShoppingListView from './components/ShoppingListView';
import AuthView from './components/AuthView';
import { checkAuth, logout } from './services/authService';
import { BarcodeIcon } from './components/icons/BarcodeIcon';
import { EditIcon } from './components/icons/EditIcon';

type ModalState =
  | 'none'
  | 'scanning'
  | 'productForm'
  | 'manualForm'
  | 'productNamePrompt';

type View = 'home' | 'list';

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(checkAuth());
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [modal, setModal] = useState<ModalState>('none');
  const [scannedBarcode, setScannedBarcode] = useState<string | null>(null);
  const [scannedProductName, setScannedProductName] = useState<string>('');
  const [currentView, setCurrentView] = useState<View>('home');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
        if (isLoggedIn) {
            setIsLoading(true);
            const fetchedProducts = await loadProducts();
            setProducts(fetchedProducts);
            setIsLoading(false);
        }
    };
    fetchProducts();
  }, [isLoggedIn]);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
    setProducts([]);
    setSelectedProduct(null);
    setCurrentView('home');
  };

  const handleScanSuccess = useCallback(async (barcode: string) => {
    setModal('none');
    setScannedBarcode(barcode);
    const existingProduct = products.find(p => p.barcode === barcode);
    if (existingProduct) {
      setSelectedProduct(existingProduct);
      setScannedProductName(existingProduct.name);
      setModal('productForm');
    } else {
      setIsLoading(true);
      const productInfo = await fetchProductInfoByBarcode(barcode);
      setIsLoading(false);
      if (productInfo) {
        setScannedProductName(productInfo?.name || '');
        setModal('productForm');
      } else {
        setErrorMessage("Could not find product information for this barcode.");
      }
    }
  }, [products]);

  const addOrUpdateProduct = async (
    barcode: string,
    name: string,
    priceEntry: { supermarket: string; price: number }
  ) => {
    const newPriceEntry: PriceEntry = {
      ...priceEntry,
      id: new Date().toISOString() + Math.random(),
      date: new Date().toISOString(),
    };

    setIsLoading(true);
    try {
        const updatedProducts = await apiAddOrUpdateProduct({ barcode, name, priceEntry: newPriceEntry });
        setProducts(updatedProducts);
        const updatedSelectedProduct = updatedProducts.find(p => p.barcode === barcode);
        setSelectedProduct(updatedSelectedProduct || null);
        setModal('none');
    } catch (e) {
        setErrorMessage("Could not save the product. The server might be busy. Please try again in a moment.");
    } finally {
        setIsLoading(false);
        setScannedBarcode(null);
        setScannedProductName('');
    }
  };

  const handleManualAddProduct = (entry: {name: string, supermarket: string, price: number}) => {
     addOrUpdateProduct(`manual_${new Date().getTime()}`, entry.name, {supermarket: entry.supermarket, price: entry.price});
  }

  const handleDeleteEntry = async (productId: string, priceEntryId: string) => {
    setIsLoading(true);
    try {
        const updatedProducts = await apiDeletePriceEntry(productId, priceEntryId);
        setProducts(updatedProducts);
        const updatedSelectedProduct = updatedProducts.find(p => p.barcode === productId);
        setSelectedProduct(updatedSelectedProduct || null);
    } catch(e) {
        setErrorMessage("Could not delete the entry. Please try again in a moment.");
    } finally {
        setIsLoading(false);
    }
  }

  const handleBackToList = () => {
    setSelectedProduct(null);
  };

  if (!isLoggedIn) {
    return <AuthView onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <Header currentView={currentView} onSetView={setCurrentView} onLogout={handleLogout} />

      <main className="container mx-auto max-w-4xl p-4">
        {isLoading && products.length === 0 && <p>Loading products...</p>}
        {currentView === 'home' && (
          <>
            {selectedProduct ? (
              <div>
                 <button onClick={handleBackToList} className="mb-4 text-brand-primary hover:underline">&larr; Back to all products</button>
                <ProductDetailView product={selectedProduct} onDeleteEntry={handleDeleteEntry} />
              </div>
            ) : (
              <div>
                 <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                    <button
                        onClick={() => setModal('scanning')}
                        className="flex items-center justify-center space-x-3 bg-brand-primary hover:bg-brand-secondary text-white font-bold py-4 px-6 rounded-lg transition-colors duration-300"
                    >
                        <BarcodeIcon className="w-6 h-6" />
                        <span>Scan Barcode</span>
                    </button>
                    <button
                        onClick={() => setModal('manualForm')}
                        className="flex items-center justify-center space-x-3 bg-gray-700 hover:bg-gray-600 text-white font-bold py-4 px-6 rounded-lg transition-colors duration-300"
                    >
                        <EditIcon className="w-6 h-6" />
                        <span>Manual Entry</span>
                    </button>
                </div>
                <ProductList products={products} onProductSelect={setSelectedProduct} />
              </div>
            )}
          </>
        )}

        {currentView === 'list' && (
          <ShoppingListView products={products} />
        )}
      </main>

      {errorMessage && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg animate-fade-in" onClick={() => setErrorMessage(null)}>
          <p className="font-bold">Error</p>
          <p>{errorMessage}</p>
        </div>
      )}

      {modal === 'scanning' && <BarcodeScannerModal onClose={() => setModal('none')} onScanSuccess={handleScanSuccess} />}

      {modal === 'productForm' && scannedBarcode && (
        <ProductFormModal
          onClose={() => setModal('none')}
          onAddProduct={(entry) => addOrUpdateProduct(scannedBarcode, scannedProductName || `Product ${scannedBarcode}`, entry)}
          barcode={scannedBarcode}
          productName={scannedProductName || `Unknown Product`}
        />
      )}

      {modal === 'manualForm' && (
        <ManualProductFormModal
            onClose={() => setModal('none')}
            onAddProduct={handleManualAddProduct}
            isLoading={isLoading}
        />
      )}
    </div>
  );
};

export default App;
