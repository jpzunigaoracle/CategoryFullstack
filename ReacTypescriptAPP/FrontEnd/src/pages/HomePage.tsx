import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { fetchComplaintData, fetchSelfClassifiedComplaints } from '../services/api';
import '../styles/HomePage.css';

const HomePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSelfClassLoading, setIsSelfClassLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selfClassError, setSelfClassError] = useState<string | null>(null);
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

  const handleSelfClassClick = async () => {
    setIsSelfClassLoading(true);
    setSelfClassError(null);
    
    try {
      // Get the full response directly
      const response = await axios.get('http://localhost:5000/api/analyze-complaints/classtype');
      
      // Store the entire response
      localStorage.setItem('selfClassResults', JSON.stringify(response.data));
      
      navigate('/selfclass-analysis');
    } catch (err) {
      setSelfClassError('Failed to fetch and analyze data. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsSelfClassLoading(false);
    }
  };

  const handleVisualizationClick = () => {
    navigate('/visualization');
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
          <h2>AI Self Classification</h2>
          <p>Let OCI generative AI to classify your costumer complains</p>
          <button 
            className="button" 
            onClick={handleSelfClassClick}
            disabled={isSelfClassLoading}
          >
            {isSelfClassLoading ? 'Analyzing...' : 'Start Analysis'}
          </button>
          {selfClassError && <p className="error-message">{selfClassError}</p>}
        </div>
        
        <div className="option-card">
          <h2>Data Visualization</h2>
          <p>View charts and graphs of customer sentiment and costumer complain type trends.</p>
          <button 
            className="button" 
            onClick={handleVisualizationClick}
          >
            View Analytics
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;