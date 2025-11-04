import React, { useState, useEffect } from 'react';
import { Product } from './types';
import { getProducts, savePriceData, findProductByBarcode, deletePriceEntry } from './services/storageService';
import { fetchProductInfoByBarcode } from './services/productInfoService';
import Header from './components/Header';
import ProductFormModal from './components/ProductFormModal';
import BarcodeScannerModal from './components/BarcodeScannerModal';
import ProductDetailView from './components/ProductDetailView';
import ProductList from './components/ProductList';
import ManualProductFormModal from './components/ManualProductFormModal';
import { BarcodeIcon } from './components/icons/BarcodeIcon';
import { SearchIcon } from './components/icons/SearchIcon';
import { ListIcon } from './components/icons/ListIcon';
import { EditIcon } from './components/icons/EditIcon';

type View = 'home' | 'scanning' | 'adding' | 'viewing' | 'list' | 'addingManually';
type ScanMode = 'register' | 'search';

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [view, setView] = useState<View>('home');
  const [scanMode, setScanMode] = useState<ScanMode>('search');
  const [scannedData, setScannedData] = useState<{ barcode: string; name: string } | null>(null);
  const [activeProduct, setActiveProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setProducts(getProducts());
  }, []);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleStartScan = (mode: ScanMode) => {
    setScanMode(mode);
    setView('scanning');
  };

  const handleScanSuccess = async (barcode: string) => {
    setView('home');
    setIsLoading(true);
    setError(null);
    
    if (scanMode === 'register') {
      const productInfo = await fetchProductInfoByBarcode(barcode);
      if (productInfo && productInfo.name) {
        setScannedData({ barcode, name: productInfo.name });
        setView('adding');
      } else {
        setError(`Could not find product information for barcode ${barcode}. You can try adding it manually.`);
      }
    } else { // search mode
      const product = findProductByBarcode(barcode);
      if (product) {
        setActiveProduct(product);
        setView('viewing');
      } else {
        setError(`Product with barcode ${barcode} not found in your database. Please register it first.`);
      }
    }
    setIsLoading(false);
  };
  
  const handleAddProduct = (entry: { supermarket: string; price: number; }) => {
    if (!scannedData) return;
    const updatedProducts = savePriceData({ barcode: scannedData.barcode, name: scannedData.name, ...entry });
    setProducts(updatedProducts);
    setView('home');
    setScannedData(null);
  };

  const handleAddManualProduct = (entry: { name: string; supermarket: string; price: number }) => {
    const updatedProducts = savePriceData(entry);
    setProducts(updatedProducts);
    setView('home');
  };
  
  const handleDeletePriceEntry = (productId: string, priceEntryId: string) => {
    if (!window.confirm("Are you sure you want to delete this price entry?")) {
      return;
    }
    const updatedProducts = deletePriceEntry(productId, priceEntryId);
    setProducts(updatedProducts);

    const stillExistingProduct = updatedProducts.find(p => p.barcode === productId);
    if (stillExistingProduct) {
      setActiveProduct(stillExistingProduct);
    } else {
      setActiveProduct(null);
      setView('list'); 
    }
  };

  const handleProductSelect = (product: Product) => {
    setActiveProduct(product);
    setView('viewing');
  };

  const renderHome = () => (
    <div className="text-center py-10 px-4">
      <h2 className="text-3xl font-bold text-gray-200 mb-4">What would you like to do?</h2>
      <p className="text-gray-400 mb-10 max-w-xl mx-auto">Select an option to track prices or look up a saved product.</p>
      
      {isLoading && (
        <div className="flex justify-center items-center my-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary"></div>
          <p className="ml-3 text-gray-300">Processing...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-500/20 text-red-300 p-3 rounded-md mb-6 max-w-2xl mx-auto">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        <button onClick={() => handleStartScan('register')} className="bg-gray-800 p-8 rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-300 transform hover:-translate-y-1 border border-gray-700 flex flex-col items-center justify-center">
          <BarcodeIcon className="w-12 h-12 text-brand-primary mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Register Item</h3>
          <p className="text-gray-400">Scan a barcode to add a new price entry.</p>
        </button>
        <button onClick={() => handleStartScan('search')} className="bg-gray-800 p-8 rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-300 transform hover:-translate-y-1 border border-gray-700 flex flex-col items-center justify-center">
          <SearchIcon className="w-12 h-12 text-brand-secondary mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Search Item</h3>
          <p className="text-gray-400">Scan a barcode to view its price history.</p>
        </button>
        <button onClick={() => setView('addingManually')} className="bg-gray-800 p-8 rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-300 transform hover:-translate-y-1 border border-gray-700 flex flex-col items-center justify-center">
          <EditIcon className="w-12 h-12 text-green-400 mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Add Manually</h3>
          <p className="text-gray-400">Enter details for an item without a barcode.</p>
        </button>
        <button onClick={() => setView('list')} className="bg-gray-800 p-8 rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-300 transform hover:-translate-y-1 border border-gray-700 flex flex-col items-center justify-center">
          <ListIcon className="w-12 h-12 text-gray-300 mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">View All Products</h3>
          <p className="text-gray-400">Browse and search all your saved items.</p>
        </button>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'viewing':
        return activeProduct && <ProductDetailView product={activeProduct} onDeleteEntry={handleDeletePriceEntry} />;
      case 'list':
        return <ProductList products={products} onProductSelect={handleProductSelect} />;
      case 'home':
      default:
        return renderHome();
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 font-sans">
      <Header showHomeButton={view !== 'home'} onHomeClick={() => setView('home')} />
      <main className="container mx-auto p-4 md:p-6">
        {renderContent()}
      </main>
      
      {view === 'scanning' && (
        <BarcodeScannerModal 
          onClose={() => setView('home')}
          onScanSuccess={handleScanSuccess}
        />
      )}

      {view === 'adding' && scannedData && (
        <ProductFormModal
          onClose={() => setView('home')}
          onAddProduct={handleAddProduct}
          barcode={scannedData.barcode}
          productName={scannedData.name}
        />
      )}

      {view === 'addingManually' && (
        <ManualProductFormModal
          onClose={() => setView('home')}
          onAddProduct={handleAddManualProduct}
        />
      )}
    </div>
  );
};

export default App;