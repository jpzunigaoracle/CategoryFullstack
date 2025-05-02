import axios from 'axios';
import { MODEL_NAMES, DEFAULT_MODEL } from '../utils/llm_config';

// Define interfaces
export interface SentimentAnalysisRequest {
  text: string;
  modelName?: string; // Use string type with the model names from llm_config
}

export interface SentimentAnalysisResult {
  id: string;
  summary: string;
  sentiment_score: number;
  date_created: string;
  time_created: string;
  date_ended: string;
  time_ended: string;
}

// Base URL for backend API
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Analyzes text for sentiment using the backend service
 * @param request The request containing text to analyze
 * @returns Promise with sentiment analysis results
 */
export const analyzeSentiment = async (
  request: SentimentAnalysisRequest
): Promise<SentimentAnalysisResult[]> => {
  try {
    // Use the model name only, let backend handle the configuration
    const modelName = request.modelName || DEFAULT_MODEL;
    
    // Call the backend API with the text and model name only
    const response = await axios.post(`${API_BASE_URL}/analyze-sentiment`, {
      text: request.text,
      modelName
      // No longer passing promptTemplate - backend will handle this
    });
    
    return response.data;
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    throw error;
  }
};