import React, { useState, useEffect } from 'react';
import { Product } from './types';
import { getProducts, addProductEntry, findProductByBarcode } from './services/storageService';
import { fetchProductInfoByBarcode } from './services/productInfoService';
import Header from './components/Header';
import ProductFormModal from './components/ProductFormModal';
import BarcodeScannerModal from './components/BarcodeScannerModal';
import ProductDetailView from './components/ProductDetailView';
import { BarcodeIcon } from './components/icons/BarcodeIcon';
import { SearchIcon } from './components/icons/SearchIcon';

type View = 'home' | 'scanning' | 'adding' | 'viewing';
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
        setError(`Could not find product information for barcode ${barcode}. Please try a different product or check the barcode.`);
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
    const updatedProducts = addProductEntry({ ...scannedData, ...entry });
    setProducts(updatedProducts);
    setView('home');
    setScannedData(null);
  };
  
  const renderHome = () => (
    <div className="text-center py-10 px-4">
      <h2 className="text-3xl font-bold text-gray-200 mb-4">What would you like to do?</h2>
      <p className="text-gray-400 mb-10 max-w-xl mx-auto">Select an option to start tracking prices or look up a product you've already saved.</p>
      
      {isLoading && (
        <div className="flex justify-center items-center my-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary"></div>
          <p className="ml-3 text-gray-300">Processing...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-500/20 text-red-300 p-3 rounded-md mb-6 max-w-xl mx-auto">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        <button onClick={() => handleStartScan('register')} className="bg-gray-800 p-8 rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-300 transform hover:-translate-y-1 border border-gray-700">
          <BarcodeIcon className="w-12 h-12 mx-auto text-brand-primary mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Register Item</h3>
          <p className="text-gray-400">Scan a barcode to add a new price entry for a product.</p>
        </button>
        <button onClick={() => handleStartScan('search')} className="bg-gray-800 p-8 rounded-lg shadow-lg hover:bg-gray-700/80 transition-all duration-300 transform hover:-translate-y-1 border border-gray-700">
          <SearchIcon className="w-12 h-12 mx-auto text-brand-secondary mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Search Item</h3>
          <p className="text-gray-400">Scan a barcode to view its price history and details.</p>
        </button>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'viewing':
        return activeProduct && <ProductDetailView product={activeProduct} onClose={() => setView('home')} />;
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
    </div>
  );
};

export default App;