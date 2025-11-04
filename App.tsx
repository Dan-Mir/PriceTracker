import React, { useState, useEffect } from 'react';
import { Product, PriceEntry } from './types';
import { getProducts, saveProducts } from './services/storageService';
import { fetchProductInfoByBarcode } from './services/productInfoService';
import Header from './components/Header';
import ProductList from './components/ProductList';
import ProductDetailView from './components/ProductDetailView';
import BarcodeScannerModal from './components/BarcodeScannerModal';
import ProductFormModal from './components/ProductFormModal';
import ManualProductFormModal from './components/ManualProductFormModal';
import ShoppingListView from './components/ShoppingListView';
import { BarcodeIcon } from './components/icons/BarcodeIcon';
import { EditIcon } from './components/icons/EditIcon';
import { ShoppingCartIcon } from './components/icons/ShoppingCartIcon';
import { ListIcon } from './components/icons/ListIcon';

type View = 'list' | 'detail' | 'shopping';
type Modal = 'scanner' | 'addProduct' | 'manualAdd' | null;

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [currentView, setCurrentView] = useState<View>('list');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [activeModal, setActiveModal] = useState<Modal>(null);
  const [scannedBarcode, setScannedBarcode] = useState<string | null>(null);
  const [isLoadingProductInfo, setIsLoadingProductInfo] = useState(false);

  useEffect(() => {
    setProducts(getProducts());
  }, []);

  useEffect(() => {
    saveProducts(products);
  }, [products]);

  const handleProductSelect = (product: Product) => {
    setSelectedProduct(product);
    setCurrentView('detail');
  };
  
  const handleGoHome = () => {
    setSelectedProduct(null);
    setCurrentView('list');
  };
  
  const handleScanSuccess = async (barcode: string) => {
    setActiveModal(null);
    const existingProduct = products.find(p => p.barcode === barcode);
    if (existingProduct) {
      setSelectedProduct(existingProduct);
      setScannedBarcode(barcode);
      setActiveModal('addProduct');
    } else {
      setIsLoadingProductInfo(true);
      const productInfo = await fetchProductInfoByBarcode(barcode);
      setIsLoadingProductInfo(false);
      if (productInfo) {
        const newProduct: Product = {
          barcode,
          name: productInfo.name,
          priceHistory: [],
        };
        // Add product first to get it in the list, then open modal
        setProducts(prev => [...prev, newProduct]);
        setSelectedProduct(newProduct);
        setScannedBarcode(barcode);
        setActiveModal('addProduct');
      } else {
        alert(`Could not find product information for barcode: ${barcode}. You may need to add it manually.`);
      }
    }
  };

  const handleAddPriceEntry = (entry: { supermarket: string; price: number; }) => {
    if (!selectedProduct) return;

    const newPriceEntry: PriceEntry = {
      ...entry,
      id: new Date().toISOString(),
      date: new Date().toISOString(),
    };
    
    setProducts(prevProducts => {
        const updatedProducts = prevProducts.map(p => {
            if (p.barcode === selectedProduct.barcode) {
                return { ...p, priceHistory: [...p.priceHistory, newPriceEntry] };
            }
            return p;
        });
        const updatedSelectedProduct = updatedProducts.find(p => p.barcode === selectedProduct.barcode);
        if (updatedSelectedProduct) {
            setSelectedProduct(updatedSelectedProduct);
        }
        return updatedProducts;
    });

    setActiveModal(null);
    setScannedBarcode(null);
  };
  
  const handleAddManualProduct = (entry: { name: string; supermarket: string; price: number; }) => {
      const newPriceEntry: PriceEntry = {
          supermarket: entry.supermarket,
          price: entry.price,
          id: new Date().toISOString(),
          date: new Date().toISOString(),
      };
      
      const newProduct: Product = {
          name: entry.name,
          barcode: `manual_${new Date().getTime()}`, // unique ID for manual entries
          priceHistory: [newPriceEntry],
      };
      
      setProducts(prev => [...prev, newProduct]);
      setActiveModal(null);
  };

  const handleDeleteEntry = (productId: string, priceEntryId: string) => {
    if (!window.confirm("Are you sure you want to delete this price entry?")) return;

    setProducts(prevProducts => {
      const updatedProducts = prevProducts.map(p => {
        if (p.barcode === productId) {
          const updatedHistory = p.priceHistory.filter(e => e.id !== priceEntryId);
          return { ...p, priceHistory: updatedHistory };
        }
        return p;
      }).filter(p => p.priceHistory.length > 0 || !p.barcode.startsWith('manual_')); // Remove product if it has no history, unless it was a scanned one

      const updatedSelectedProduct = updatedProducts.find(p => p.barcode === selectedProduct?.barcode);
      if (updatedSelectedProduct) {
        setSelectedProduct(updatedSelectedProduct);
      } else {
        // If the selected product was deleted
        handleGoHome();
      }
      return updatedProducts;
    });
  };

  const renderView = () => {
    switch(currentView) {
      case 'detail':
        return selectedProduct && <ProductDetailView product={selectedProduct} onDeleteEntry={handleDeleteEntry} />;
      case 'shopping':
        return <ShoppingListView products={products} />;
      case 'list':
      default:
        return <ProductList products={products} onProductSelect={handleProductSelect} />;
    }
  };

  return (
    <div className="bg-gray-900 min-h-screen text-gray-200 font-sans pb-24">
      <Header showHomeButton={currentView !== 'list'} onHomeClick={handleGoHome} />
      <main className="container mx-auto p-4 md:p-6">
        {isLoadingProductInfo && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <p className="text-white text-xl">Fetching product info...</p>
            </div>
        )}
        {renderView()}
      </main>
      <footer className="fixed bottom-0 left-0 right-0 bg-gray-800/80 backdrop-blur-sm shadow-top p-2 border-t border-gray-700">
        <div className="container mx-auto flex justify-center items-center space-x-4">
           <button 
                onClick={() => setCurrentView('list')}
                className={`flex flex-col items-center space-y-1 p-2 rounded-lg transition-colors w-24 ${currentView === 'list' ? 'text-brand-primary' : 'text-gray-400 hover:text-white'}`}
            >
                <ListIcon className="w-6 h-6" />
                <span className="text-xs font-medium">Products</span>
            </button>
            <button 
                onClick={() => setActiveModal('scanner')}
                className="bg-brand-primary hover:bg-brand-secondary text-white rounded-full p-4 transform -translate-y-6 shadow-lg border-4 border-gray-900"
                aria-label="Scan new barcode"
            >
                <BarcodeIcon className="w-8 h-8"/>
            </button>
             <button 
                onClick={() => setCurrentView('shopping')}
                className={`flex flex-col items-center space-y-1 p-2 rounded-lg transition-colors w-24 ${currentView === 'shopping' ? 'text-brand-primary' : 'text-gray-400 hover:text-white'}`}
            >
                <ShoppingCartIcon className="w-6 h-6" />
                <span className="text-xs font-medium">Shopping List</span>
            </button>
        </div>
      </footer>
      
      {/* Modals */}
      {activeModal === 'scanner' && <BarcodeScannerModal onClose={() => setActiveModal(null)} onScanSuccess={handleScanSuccess} />}
      {activeModal === 'addProduct' && selectedProduct && (
        <ProductFormModal 
          onClose={() => { setActiveModal(null); setScannedBarcode(null); }}
          onAddProduct={handleAddPriceEntry}
          barcode={selectedProduct.barcode}
          productName={selectedProduct.name}
        />
      )}
      {activeModal === 'manualAdd' && (
        <ManualProductFormModal 
          onClose={() => setActiveModal(null)}
          onAddProduct={handleAddManualProduct}
        />
      )}
       {/* Floating action button for manual add on list view */}
      {currentView === 'list' && (
          <button
              onClick={() => setActiveModal('manualAdd')}
              className="fixed bottom-24 right-6 bg-brand-secondary hover:bg-brand-secondary/80 text-white rounded-full p-4 shadow-lg"
              aria-label="Add product manually"
          >
              <EditIcon className="w-6 h-6" />
          </button>
      )}
    </div>
  );
};

export default App;
