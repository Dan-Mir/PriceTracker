import React, { useState, useEffect, useCallback } from 'react';
import { Product, PriceEntry } from './types';
import { loadProducts, saveProducts } from './services/storageService';
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
  const [isLoadingProductInfo, setIsLoadingProductInfo] = useState(false);

  useEffect(() => {
    if (isLoggedIn) {
      setProducts(loadProducts());
    }
  }, [isLoggedIn]);

  useEffect(() => {
    if (isLoggedIn) {
        saveProducts(products);
    }
  }, [products, isLoggedIn]);

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
      setIsLoadingProductInfo(true);
      const productInfo = await fetchProductInfoByBarcode(barcode);
      setIsLoadingProductInfo(false);
      setScannedProductName(productInfo?.name || '');
      setModal('productForm');
    }
  }, [products]);

  const addOrUpdateProduct = (
    barcode: string,
    name: string,
    priceEntry: { supermarket: string; price: number }
  ) => {
    const newPriceEntry: PriceEntry = {
      ...priceEntry,
      id: new Date().toISOString() + Math.random(),
      date: new Date().toISOString(),
    };

    setProducts(prevProducts => {
      const existingProductIndex = prevProducts.findIndex(p => p.barcode === barcode);
      let newProducts = [...prevProducts];

      if (existingProductIndex > -1) {
        const updatedProduct = { ...newProducts[existingProductIndex] };
        updatedProduct.priceHistory = [...updatedProduct.priceHistory, newPriceEntry];
        newProducts[existingProductIndex] = updatedProduct;
        setSelectedProduct(updatedProduct);
      } else {
        const newProduct: Product = {
          barcode,
          name,
          priceHistory: [newPriceEntry],
        };
        newProducts.push(newProduct);
        setSelectedProduct(newProduct);
      }
      return newProducts;
    });

    setModal('none');
    setScannedBarcode(null);
    setScannedProductName('');
  };

  const handleManualAddProduct = (entry: {name: string, supermarket: string, price: number}) => {
     addOrUpdateProduct(`manual_${new Date().getTime()}`, entry.name, {supermarket: entry.supermarket, price: entry.price});
  }

  const handleDeleteEntry = (productId: string, priceEntryId: string) => {
    setProducts(prevProducts => {
        const newProducts = prevProducts.map(p => {
            if (p.barcode === productId) {
                const updatedHistory = p.priceHistory.filter(e => e.id !== priceEntryId);
                return { ...p, priceHistory: updatedHistory };
            }
            return p;
        }).filter(p => p.priceHistory.length > 0); // Remove product if it has no price entries left

        const currentSelected = selectedProduct;
        if(currentSelected && currentSelected.barcode === productId) {
            const updatedSelectedProduct = newProducts.find(p => p.barcode === productId);
            setSelectedProduct(updatedSelectedProduct || null);
        }

        return newProducts;
    });
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

      {modal === 'scanning' && <BarcodeScannerModal onClose={() => setModal('none')} onScanSuccess={handleScanSuccess} />}
      
      {isLoadingProductInfo && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
            <p className="text-xl">Fetching product info...</p>
        </div>
      )}

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
        />
      )}
    </div>
  );
};

export default App;
