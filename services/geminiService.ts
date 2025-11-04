import { GoogleGenAI, Type } from "@google/genai";
import { AlternativeProduct, Product, ShoppingListAnalysisResult } from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY! });

const suggestionsSchema = {
  type: Type.ARRAY,
  items: {
    type: Type.OBJECT,
    properties: {
      name: {
        type: Type.STRING,
        description: 'The name of the alternative product.'
      },
      reason: {
        type: Type.STRING,
        description: 'A brief reason why this is a good alternative.'
      }
    },
    required: ['name', 'reason'],
  }
};

const shoppingListAnalysisSchema = {
    type: Type.ARRAY,
    items: {
        type: Type.OBJECT,
        properties: {
            itemName: { type: Type.STRING, description: "The original item from the user's shopping list." },
            status: { type: Type.STRING, description: "Should be 'FOUND' or 'NOT_FOUND'." },
            matchedProductName: { type: Type.STRING, description: "The name of the product found in the database. Omit if not found." },
            bestSupermarket: { type: Type.STRING, description: "The supermarket with the lowest price. Omit if not found." },
            lowestPrice: { type: Type.NUMBER, description: "The lowest price for the matched product. Omit if not found." },
        },
        required: ['itemName', 'status'],
    }
};

export const getAlternativeSuggestions = async (productName: string): Promise<AlternativeProduct[]> => {
  try {
    const prompt = `Based on the product "${productName}", suggest 3 cheaper or healthier alternatives that can be found in a typical supermarket. Provide a brief reason for each suggestion.`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: suggestionsSchema,
      },
    });

    const jsonText = response.text.trim();
    if (!jsonText) return [];
    
    return JSON.parse(jsonText) as AlternativeProduct[];

  } catch (error) {
    console.error("Error fetching suggestions from Gemini API:", error);
    throw new Error("Failed to get suggestions from AI. Please check your API key and try again.");
  }
};

export const analyzeShoppingList = async (shoppingList: string[], products: Product[]): Promise<ShoppingListAnalysisResult[]> => {
    if (shoppingList.length === 0 || products.length === 0) {
        return shoppingList.map(item => ({ itemName: item, status: 'NOT_FOUND' }));
    }

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

    try {
        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: shoppingListAnalysisSchema,
            },
        });

        const jsonText = response.text.trim();
        if (!jsonText) throw new Error("AI returned an empty response.");
        
        return JSON.parse(jsonText) as ShoppingListAnalysisResult[];

    } catch (error) {
        console.error("Error analyzing shopping list with Gemini API:", error);
        throw new Error("Failed to get analysis from AI. Please try again.");
    }
};
