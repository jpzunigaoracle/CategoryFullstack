import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchComplaintData } from '../services/api';
import '../styles/HomePage.css';

const HomePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleAnalyzeClick = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await fetchComplaintData();
      // Store the results in localStorage for the AnalysisPage to use
      localStorage.setItem('analysisResults', JSON.stringify(data));
      navigate('/analysis');
    } catch (err) {
      setError('Failed to fetch and analyze data. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-container">
      <h1>SMEG Customer Complaint Analysis</h1>
      
      <div className="options-container">
        <div className="option-card">
          <h2>AI Sentiment Analysis</h2>
          <p>Analyze customer complaints to identify sentiment patterns and improve customer service.</p>
          <button 
            className="button" 
            onClick={handleAnalyzeClick}
            disabled={isLoading}
          >
            {isLoading ? 'Analyzing...' : 'Start Analysis'}
          </button>
          {error && <p className="error-message">{error}</p>}
        </div>
        
        <div className="option-card">
          <h2>Data Visualization</h2>
          <p>View charts and graphs of customer sentiment trends over time.</p>
          <button className="button" disabled>Coming Soon</button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;