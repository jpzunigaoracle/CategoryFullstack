import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { fetchComplaintData } from '../services/api';
import '../styles/HomePage.css';
import OCIPoweredBadge from '../components/OCIPoweredBadge';

const HomePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSelfClassLoading, setIsSelfClassLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selfClassError, setSelfClassError] = useState<string | null>(null);
  const [showAnimation, setShowAnimation] = useState<boolean>(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Intro animation timing
    const timer = setTimeout(() => {
      setShowAnimation(false);
    }, 2000);
    
    return () => clearTimeout(timer);
  }, []);

  const handleAnalyzeClick = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await fetchComplaintData();
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
      const response = await axios.get('http://localhost:5000/api/analyze-complaints/classtype');
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
      {showAnimation ? (
        <div className="intro-animation">
          <div className="logo-container">
            <div className="logo">
              <span className="logo-text">CC</span>
            </div>
            <h1 className="animate-text">Chat-Classifier</h1>
          </div>
        </div>
      ) : (
        <>
          <header className="app-header">
            
              <span></span>
            
            
            
          </header>

          <div className="tagline">
            <h2>Let the machine do all analytics for you, from whatever customer dialog you have</h2>
          </div>
          
          <div className="options-container">
            <div className="option-card" onClick={handleAnalyzeClick}>
              <div className="card-icon sentiment-icon">
                <i className="icon-sentiment"></i>
              </div>
              <h3>AI Sentiment Analysis</h3>
              <p>Analyze customer complaints to identify sentiment patterns and improve customer service.</p>
              <button 
                className="button primary-button" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <><span className="spinner"></span> Analyzing...</>
                ) : (
                  'Start Analysis'
                )}
              </button>
              {error && <p className="error-message">{error}</p>}
            </div>
            
            <div className="option-card" onClick={handleSelfClassClick}>
              <div className="card-icon classify-icon">
                <i className="icon-classify"></i>
              </div>
              <h3>AI Self Classification</h3>
              <p>Let OCI Generative AI classify your customer complaints automatically.</p>
              <button 
                className="button primary-button" 
                disabled={isSelfClassLoading}
              >
                {isSelfClassLoading ? (
                  <><span className="spinner"></span> Analyzing...</>
                ) : (
                  'Start Analysis'
                )}
              </button>
              {selfClassError && <p className="error-message">{selfClassError}</p>}
            </div>
            
            <div className="option-card" onClick={handleVisualizationClick}>
              <div className="card-icon visualize-icon">
                <i className="icon-visualize"></i>
              </div>
              <h3>Data Visualization</h3>
              <p>View charts and graphs of customer sentiment and complaint type trends.</p>
              <button className="button secondary-button">
                View Analytics
              </button>
            </div>
          </div>

          <footer className="app-footer">
            <div className="footer-content">
              <p>© 2023 Chat-Classifier | A SMEG Customer Complaint Analysis Tool</p>
              <p className="oci-footer">Built with OCI Generative AI</p>
            </div>
          </footer>
        </>
      )}
    </div>
  );
};

export default HomePage;