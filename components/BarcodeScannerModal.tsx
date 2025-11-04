import React, { useEffect, useRef, useState } from 'react';
import { XIcon } from './icons/XIcon';

interface BarcodeScannerModalProps {
  onClose: () => void;
  onScanSuccess: (barcode: string) => void;
}

const BarcodeScannerModal: React.FC<BarcodeScannerModalProps> = ({ onClose, onScanSuccess }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isApiSupported, setIsApiSupported] = useState(true);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (!('BarcodeDetector' in window)) {
      setIsApiSupported(false);
      setError("Your browser doesn't support barcode scanning. Try Chrome on Android or desktop.");
      return;
    }

    const detector = new (window as any).BarcodeDetector({ formats: ['ean_13', 'upc_a', 'ean_8'] });
    let animationFrameId: number;

    const startScan = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment' } 
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }

        const detect = async () => {
          try {
            if (videoRef.current && videoRef.current.readyState >= 2) {
                const barcodes = await detector.detect(videoRef.current);
                if (barcodes.length > 0) {
                  onScanSuccess(barcodes[0].rawValue);
                  return;
                }
            }
          } catch(e) {
            console.error("Detection failed:", e);
          }
          animationFrameId = requestAnimationFrame(detect);
        };
        detect();

      } catch (err) {
        console.error("Camera access error:", err);
        setError("Could not access camera. Please grant permission and try again.");
      }
    };

    startScan();

    return () => {
      cancelAnimationFrame(animationFrameId);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [onScanSuccess]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center z-50 animate-fade-in">
      <div className="relative w-full max-w-2xl aspect-video rounded-lg overflow-hidden shadow-2xl">
        <video ref={videoRef} className="w-full h-full object-cover" muted playsInline />
        <div className="absolute inset-0 border-8 border-white/20 rounded-lg pointer-events-none"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4/5 h-1/3 border-2 border-red-500 rounded-lg shadow-lg pointer-events-none"></div>
      </div>
      <p className="mt-4 text-white text-lg font-semibold">Point camera at a barcode</p>
      {error && <p className="mt-2 text-red-400 bg-red-900/50 px-4 py-2 rounded-md">{error}</p>}
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 bg-black/50 rounded-full p-3 text-white hover:bg-black/80"
        aria-label="Close scanner"
      >
        <XIcon className="w-6 h-6"/>
      </button>
    </div>
  );
};

export default BarcodeScannerModal;
