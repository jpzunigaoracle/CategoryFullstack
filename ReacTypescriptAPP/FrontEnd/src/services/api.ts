import axios from 'axios';

export interface ComplaintData {
  DialogID: string;
  DateCreated: string;
  "Date&TimeCreated": string;
  DateEnded: string;
  "Date&TimeEnded": string;
  CustomerComplaintDialog: string;
}

export interface SentimentResult {
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
 * Fetches complaint data and performs sentiment analysis using OCI AI
 * @returns Promise with sentiment analysis results
 */
export const fetchComplaintData = async (): Promise<SentimentResult[]> => {
  try {
    // Call the backend API to analyze complaints using OCI AI
    const response = await axios.get(`${API_BASE_URL}/analyze-complaints`);
    
    if (response.data && Array.isArray(response.data)) {
      return response.data;
    } else if (response.data && response.data.reports && Array.isArray(response.data.reports)) {
      return response.data.reports;
    } else {
      throw new Error('Invalid response format from API');
    }
  } catch (error) {
    console.error('Error fetching complaint data:', error);
    throw error;
  }
};

/**
 * Fetches raw complaints data without analysis
 * @returns Promise with raw complaint data
 */
export const fetchRawComplaints = async (): Promise<ComplaintData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/complaints`);
    return response.data;
  } catch (error) {
    console.error('Error fetching raw complaints:', error);
    throw error;
  }
};