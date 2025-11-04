
import { GoogleGenAI, Type } from "@google/genai";
import { AlternativeProduct } from "../types";

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.warn("API_KEY environment variable not set. Gemini features will be disabled.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

export const getAlternativeSuggestions = async (productName: string): Promise<AlternativeProduct[]> => {
  if (!API_KEY) {
    throw new Error("API key is not configured.");
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: `Given the product "${productName}", suggest 5 alternative products I could look for in a supermarket. Provide the product name and a brief reason why it's a good alternative.`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              name: {
                type: Type.STRING,
                description: 'The name of the alternative product.',
              },
              reason: {
                type: Type.STRING,
                description: 'A brief reason why this is a good alternative.',
              },
            },
            required: ["name", "reason"],
          },
        },
      },
    });

    const jsonText = response.text.trim();
    const suggestions = JSON.parse(jsonText);
    return suggestions as AlternativeProduct[];

  } catch (error) {
    console.error("Error fetching suggestions from Gemini API:", error);
    throw new Error("Failed to get suggestions. Please try again.");
  }
};
