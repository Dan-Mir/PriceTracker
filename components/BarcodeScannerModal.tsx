import React, { useEffect, useState } from 'react';
import { BarcodeScanner } from '@capacitor-mlkit/barcode-scanning';
import { XIcon } from './icons/XIcon';

interface BarcodeScannerModalProps {
  onClose: () => void;
  onScanSuccess: (barcode: string) => void;
}

const BarcodeScannerModal: React.FC<BarcodeScannerModalProps> = ({ onClose, onScanSuccess }) => {
  const [error, setError] = useState<string | null>(null);

  const handleClose = () => {
    BarcodeScanner.stopScan?.();
    onClose();
  };

  useEffect(() => {
    const performScan = async () => {
      try {
        const permissionStatus = await BarcodeScanner.requestPermissions();
        if (permissionStatus.camera !== 'granted') {
          setError("Camera permission is required for scanning. Please grant permission in settings.");
          return;
        }

        document.documentElement.classList.add('scanner-active');
        document.body.classList.add('scanner-active');
        document.getElementById('root')?.classList.add('scanner-active');

        const { barcodes } = await BarcodeScanner.scan();

        if (barcodes.length > 0) {
          onScanSuccess(barcodes[0].displayValue);
        }
      } catch (e: any) {
        console.error(e);
        setError('An error occurred during the scan.');
      } finally {
        document.documentElement.classList.remove('scanner-active');
        document.body.classList.remove('scanner-active');
        document.getElementById('root')?.classList.remove('scanner-active');
        onClose();
      }
    };

    performScan();

    return () => {
        BarcodeScanner.stopScan?.();
    }

  }, [onClose, onScanSuccess]);


  return (
    <>
    <style>{`
      html.scanner-active {
        background: transparent !important;
      }
      body.scanner-active {
        background: transparent !important;
      }
      #root.scanner-active {
        background: transparent !important;
      }
    `}</style>
    <div className="fixed inset-0 bg-transparent flex flex-col items-center justify-center z-50">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4/5 h-1/3 border-2 border-red-500 rounded-lg shadow-lg pointer-events-none" aria-hidden="true"></div>

      {error && (
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-4/5 text-center text-white bg-red-900/80 p-4 rounded-lg">
          <p className="font-bold">Permission Error</p>
          <p>{error}</p>
        </div>
      )}

      <button 
        onClick={handleClose}
        className="absolute top-5 right-5 bg-black/50 rounded-full p-3 text-white"
        aria-label="Close scanner"
      >
        <XIcon className="w-8 h-8"/>
      </button>
    </div>
    </>
  );
};

export default BarcodeScannerModal;
