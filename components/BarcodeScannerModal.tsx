import React, { useEffect, useState, useCallback } from 'react';
import { BarcodeScanner, BarcodeScannerPermissionState } from '@capacitor-community/barcode-scanner';
import { XIcon } from './icons/XIcon';

interface BarcodeScannerModalProps {
  onClose: () => void;
  onScanSuccess: (barcode: string) => void;
}

const BarcodeScannerModal: React.FC<BarcodeScannerModalProps> = ({ onClose, onScanSuccess }) => {
  const [error, setError] = useState<string | null>(null);

  const stopScan = useCallback(async () => {
    try {
      document.body.classList.remove('scanner-active');
      await BarcodeScanner.stopScan();
    } catch (e) {
      console.error("Error stopping scanner:", e);
    }
  }, []);

  const handleClose = useCallback(() => {
    stopScan();
    onClose();
  }, [stopScan, onClose]);

  useEffect(() => {
    const startScan = async () => {
      try {
        // First, check the current permission status without forcing a prompt
        const status: BarcodeScannerPermissionState = await BarcodeScanner.checkPermission();

        if (status.denied) {
          // The user has previously denied permission.
          setError("Camera permission is required. Please enable it in your app settings.");
          return;
        }

        // If permission is not granted, this will prompt the user.
        await BarcodeScanner.checkPermission({ force: true });

        // Hide the webview background to show the camera
        await BarcodeScanner.hideBackground();
        document.body.classList.add('scanner-active');

        const result = await BarcodeScanner.startScan();

        if (result.hasContent) {
          onScanSuccess(result.content!);
        } else {
          // Handle case where user closes scanner without scanning
          handleClose();
        }
      } catch (e: any) {
        setError("An unexpected error occurred while trying to start the scanner.");
        console.error(e);
      }
    };

    startScan();

    // Cleanup function to stop the scanner when the component unmounts
    return () => {
      stopScan();
    };
  }, [onScanSuccess, handleClose, stopScan]);


  return (
    <>
    <style>{`
      body.scanner-active {
        background: transparent !important;
        opacity: 0; /* Hide web content to show camera view */
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
