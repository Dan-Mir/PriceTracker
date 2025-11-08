# PriceTracker: AI-Powered Supermarket Price Tracker

PriceTracker is a modern web application designed to help users track and compare product prices across various supermarkets. By leveraging barcode scanning, manual entry, and a powerful AI assistant, users can make smarter shopping decisions and find the best deals.

This application is built with React, TypeScript, and Tailwind CSS, and it runs entirely in the browser, using local storage for data persistence.

![PriceTracker Application Screenshot](https://storage.googleapis.com/aistudio-hosting/docs/images/pricewise_screenshot.png)

---

## ✨ Key Features

- **Multi-User Account System**: Securely register and log in to a personal account. All your data is tied to your profile.
- **Barcode Scanning**: Quickly add products by scanning their barcodes using your device's camera.
- **Automatic Product Info**: The app automatically fetches the product's name from the Open Food Facts database after a successful scan.
- **Manual Entry**: Easily add items without a barcode, such as fresh fruit, vegetables, or deli products.
- **Comprehensive Price History**: Track every price entry for a product, showing the supermarket, price, and date.
- **Product Dashboard**: View an alphabetized, searchable list of all your tracked products.
- **Detailed Analytics**: See the lowest, highest, and latest prices for any product at a glance.
- **AI Shopping List Assistant**: Create a shopping list, and let the Gemini-powered AI analyze your price history to recommend the cheapest supermarket for each item.
- **AI Product Alternatives**: Get intelligent suggestions for cheaper or healthier alternatives to your tracked products.
- **Persistent Data**: All your products and shopping lists are saved in your browser's local storage, specific to your user account.
- **Modern & Responsive UI**: A clean, intuitive interface built with Tailwind CSS that works beautifully on both desktop and mobile devices.

---

## 🛠️ Technology Stack

- **Frontend**: React, TypeScript
- **Styling**: Tailwind CSS
- **AI/ML**: Google Gemini API
- **External Data**: Open Food Facts API (for barcode lookups)
- **Browser APIs**:
  - Barcode Detection API
  - Web Storage API (localStorage)
  - `navigator.mediaDevices` (for camera access)

---

## 🚀 Getting Started

This application is designed to run in a modern web browser and requires no backend server or complex build steps.

### Prerequisites

1.  A modern web browser with support for the Barcode Detection API (e.g., Chrome for Desktop/Android).
2.  A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Running the Application

1.  **API Key Configuration**: The application expects the Gemini API key to be available as an environment variable (`process.env.API_KEY`). When using a development environment like Vite or Create React App, you would typically create a `.env` file in the project root and add your key:
    ```
    API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```
    *Note: The environment this app was built in injects this variable automatically. If running locally, ensure your local server setup can provide this environment variable to the client-side code.*

2.  **Serve the Files**: Since there is no build process, you just need to serve the project files with a simple local web server.
    - If you have Node.js installed, you can use the `http-server` package.
      ```bash
      # Install http-server globally if you haven't already
      npm install -g http-server
      
      # Navigate to the project's root directory and run the server
      http-server -c-1
      ```
    - Open your browser and navigate to the local address provided by the server (e.g., `http://localhost:8080`).

---

## 📖 How to Use the App

1.  **Register/Login**: The first time you open the app, you'll see a login/register screen. Create a new account to get started. Your session will be remembered.
2.  **Add Products**:
    - **Scan Barcode**: Click "Scan Barcode" on the home screen. Grant camera permission, and point your device at a product's barcode. The app will fetch the product's name and prompt you to add the supermarket and price.
    - **Manual Entry**: Click "Manual Entry" to add items without barcodes. You'll need to provide the product name, supermarket, and price.
3.  **View & Search Products**:
    - The home screen shows a list of all your tracked items.
    - Use the search bar to filter products by name.
    - Click on any product to see its detailed view.
4.  **Analyze Price History**:
    - In the product detail view, you can see a full history of your price entries.
    - Key stats like the lowest, highest, and latest prices are highlighted.
    - You can delete any incorrect price entry by clicking the trash icon.
5.  **Use the AI Shopping List**:
    - Navigate to the "Shopping List" tab using the cart icon in the header.
    - Type items you want to buy into the text box, one per line.
    - Click "Analyze My List". The AI will compare your list against your tracked products and create an optimized shopping plan, telling you where to buy each item for the lowest price.
    - As you shop, you can check items off your list.

---

## 📂 File Structure

The project is organized into logical directories for components, services, and types.

```
/
├── components/
│   ├── icons/                # Reusable SVG icon components
│   ├── AuthView.tsx          # Login/Register screen
│   ├── BarcodeScannerModal.tsx # Camera view for scanning barcodes
│   ├── GeminiSuggestions.tsx  # Component to fetch AI alternatives
│   ├── Header.tsx            # App header with navigation
│   ├── ManualProductFormModal.tsx # Form for non-barcoded items
│   ├── ProductDetailView.tsx # Detailed view of a single product
│   ├── ProductFormModal.tsx  # Form to add price after scanning
│   ├── ProductList.tsx       # Searchable list of all products
│   └── ShoppingListView.tsx  # AI-powered shopping list feature
│
├── services/
│   ├── authService.ts        # Handles user login/register logic
│   ├── geminiService.ts      # Manages all calls to the Gemini API
│   ├── productInfoService.ts # Fetches data from Open Food Facts API
│   └── storageService.ts     # Manages all interactions with localStorage
│
├── types.ts                  # Centralized TypeScript type definitions
├── App.tsx                   # Main application component and state management
├── index.html                # The single HTML page entry point
├── index.tsx                 # React application root
└── README.md                 # This file
```
