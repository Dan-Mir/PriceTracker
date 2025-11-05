import React, { useEffect, useState } from 'react';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { BarcodeScanner } from '@capacitor-community/barcode-scanner';
import { XIcon } from './icons/XIcon';

interface BarcodeScannerModalProps {
  onClose: () => void;
  onScanSuccess: (barcode: string) => void;
}

const BarcodeScannerModal: React.FC<BarcodeScannerModalProps> = ({ onClose, onScanSuccess }) => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const startScan = async () => {
      try {
        await BarcodeScanner.checkPermission({ force: true });

        // Hide the webview background to show the camera
        await BarcodeScanner.hideBackground();
        document.body.classList.add('scanner-active');

        const result = await BarcodeScanner.startScan();

        if (result.hasContent) {
          onScanSuccess(result.content!);
        }
      } catch (e: any) {
        if (e.message.includes("permission was denied")) {
            setError("Camera permission is required to scan barcodes. Please grant permission in your phone's settings.");
        } else {
            setError("An unexpected error occurred with the scanner.");
        }
        console.error(e);
      }
    };

    startScan();

    return () => {
      stopScan();
    };
  }, [onScanSuccess]);

  const stopScan = async () => {
    document.body.classList.remove('scanner-active');
    await BarcodeScanner.stopScan();
  };

  const handleClose = () => {
    stopScan();
    onClose();
  };

  return (
    <>
    <style>{`
      .scanner-active {
        background: transparent !important;
      }
    `}</style>
    <div className="fixed inset-0 bg-transparent flex flex-col items-center justify-center z-50">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4/5 h-1/3 border-2 border-red-500 rounded-lg shadow-lg pointer-events-none"></div>
      <p className="mt-4 text-white text-lg font-semibold bg-black/50 p-2 rounded">Point camera at a barcode</p>
      {error && <p className="mt-2 text-red-400 bg-red-900/50 px-4 py-2 rounded-md">{error}</p>}
      <button 
        onClick={handleClose}
        className="absolute top-4 right-4 bg-black/50 rounded-full p-3 text-white hover:bg-black/80"
        aria-label="Close scanner"
      >
        <XIcon className="w-6 h-6"/>
      </button>
    </div>
    </>
  );
};

export default BarcodeScannerModal;
