require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const bcrypt = require('bcrypt');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
const port = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

app.use(cors());
app.use(bodyParser.json());

// Simple request logger middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
  next();
});

const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir);
}
const usersFilePath = path.join(dataDir, 'users.json');

const readUsers = () => {
    if (!fs.existsSync(usersFilePath)) {
        return [];
    }
    const usersData = fs.readFileSync(usersFilePath);
    return JSON.parse(usersData);
};

const writeUsers = (users) => {
    fs.writeFileSync(usersFilePath, JSON.stringify(users, null, 2));
};

const readUserProducts = (userId) => {
    const userProductsPath = path.join(dataDir, `${userId}.json`);
    if (!fs.existsSync(userProductsPath)) {
        return [];
    }
    const productsData = fs.readFileSync(userProductsPath);
    return JSON.parse(productsData);
};

const writeUserProducts = (userId, products) => {
    const userProductsPath = path.join(dataDir, `${userId}.json`);
    fs.writeFileSync(userProductsPath, JSON.stringify(products, null, 2));
};

const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token == null) return res.sendStatus(401);

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
};

app.post('/api/auth/register', async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required' });
    }

    const users = readUsers();
    if (users.find(u => u.username === username)) {
        return res.status(400).json({ message: 'User already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = { id: Date.now().toString(), username, password: hashedPassword };
    users.push(newUser);
    writeUsers(users);

    res.status(201).json({ message: 'User registered successfully' });
});

app.post('/api/auth/login', async (req, res) => {
    const { username, password } = req.body;
    const users = readUsers();
    const user = users.find(u => u.username === username);

    if (!user || !await bcrypt.compare(password, user.password)) {
        return res.status(401).json({ message: 'Invalid credentials' });
    }

    const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
});

app.get('/api/products', authenticateToken, (req, res) => {
    const products = readUserProducts(req.user.userId);
    res.json(products);
});

app.post('/api/products', authenticateToken, (req, res) => {
    const { barcode, name, priceEntry } = req.body;
    const products = readUserProducts(req.user.userId);

    const existingProductIndex = products.findIndex(p => p.barcode === barcode);

    if (existingProductIndex > -1) {
        products[existingProductIndex].priceHistory.push(priceEntry);
    } else {
        products.push({ barcode, name, priceHistory: [priceEntry] });
    }

    writeUserProducts(req.user.userId, products);
    res.status(201).json(products);
});

app.delete('/api/products/:productId/entries/:entryId', authenticateToken, (req, res) => {
    const { productId, entryId } = req.params;
    const products = readUserProducts(req.user.userId);

    const productIndex = products.findIndex(p => p.barcode === productId);
    if (productIndex > -1) {
        products[productIndex].priceHistory = products[productIndex].priceHistory.filter(e => e.id !== entryId);
        if (products[productIndex].priceHistory.length === 0) {
            products.splice(productIndex, 1);
        }
    }

    writeUserProducts(req.user.userId, products);
    res.json(products);
});

app.post('/api/barcode', authenticateToken, async (req, res) => {
    const { barcode } = req.body;
    try {
        const response = await axios.get(`https://world.openfoodfacts.org/api/v2/product/${barcode}?fields=product_name`);
        if (response.data.product && response.data.product.product_name) {
            res.json({ name: response.data.product.product_name });
        } else {
            res.status(404).json({ message: 'Product not found' });
        }
    } catch (error) {
        res.status(500).json({ message: 'Error fetching product info' });
    }
});

app.post('/api/gemini/suggestions', authenticateToken, async (req, res) => {
    const { productName } = req.body;
    try {
        const prompt = `Based on the product "${productName}", suggest 3 cheaper or healthier alternatives that can be found in a typical supermarket. Provide a brief reason for each suggestion.`;
        const model = genAI.getGenerativeModel({ model: "gemini-pro"});
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        res.json(JSON.parse(text));
    } catch (error) {
        console.error("Error fetching suggestions from Gemini API:", error);
        res.status(500).json({ message: "Failed to get suggestions from AI." });
    }
});

app.post('/api/gemini/analyze-list', authenticateToken, async (req, res) => {
    const { shoppingList, products } = req.body;
    try {
        const prompt = `
            Analyze the user's shopping list based on their personal product price database.
            For each item in the shopping list, find the best and most relevant matching product from the database.
            If a match is found, identify the supermarket with the absolute lowest price for that product from its price history.
            Shopping List: ${JSON.stringify(shoppingList)}
            Product Database: ${JSON.stringify(products)}
            Respond with a JSON array where each object represents an item from the shopping list.
            If you find a match, set status to 'FOUND' and include the matched product's name, the supermarket with the best price, and that lowest price.
            If you cannot find a reasonable match for an item in the database, set status to 'NOT_FOUND' and omit the other fields.
        `;
        const model = genAI.getGenerativeModel({ model: "gemini-pro"});
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        res.json(JSON.parse(text));
    } catch (error) {
        console.error("Error analyzing shopping list with Gemini API:", error);
        res.status(500).json({ message: "Failed to get analysis from AI." });
    }
});

app.get('/', (req, res) => {
    res.send('Backend server is running!');
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
