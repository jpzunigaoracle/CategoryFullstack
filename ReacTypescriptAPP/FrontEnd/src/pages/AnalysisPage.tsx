import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AnalysisPage.css';

interface SentimentItem {
  id: string;
  summary: string;
  sentiment_score: number;
  date_created?: string;
  time_created?: string;
  date_ended?: string;
  time_ended?: string;
}

const AnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('table');
  const [results, setResults] = useState<SentimentItem[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Try to get results from localStorage
    const storedResults = localStorage.getItem('analysisResults');
    
    if (storedResults) {
      try {
        const parsedResults = JSON.parse(storedResults);
        setResults(parsedResults);
      } catch (err) {
        console.error('Error parsing stored results:', err);
        setError('Failed to load analysis results');
      }
    } else {
      setError('No analysis results found. Please run the analysis first.');
    }
    
    setIsLoading(false);
  }, []);

  const handleBackClick = () => {
    navigate('/');
  };

  const renderTableView = () => {
    if (!results) {
      return <p>No results to display</p>;
    }

    return (
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Summary</th>
              <th>Sentiment Score</th>
              <th>Date Created</th>
              <th>Date Ended</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.summary}</td>
                <td>{item.sentiment_score}</td>
                <td>{`${item.date_created || 'N/A'} ${item.time_created || ''}`}</td>
                <td>{`${item.date_ended || 'N/A'} ${item.time_ended || ''}`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderFormattedView = () => {
    if (!results) {
      return <p>No results to display</p>;
    }

    return (
      <div className="formatted-container">
        {results.map((item) => (
          <div key={item.id} className="result-card">
            <h3>Complaint #{item.id}</h3>
            <div className="result-content">
              <div className="result-summary">
                <h4>Summary</h4>
                <p>{item.summary}</p>
                
                <h4>Sentiment Score</h4>
                <div className="sentiment-bar-container">
                  <div 
                    className="sentiment-bar" 
                    style={{ width: `${(item.sentiment_score / 10) * 100}%`, 
                             backgroundColor: getSentimentColor(item.sentiment_score) }}
                  ></div>
                </div>
                <p>{item.sentiment_score}/10</p>
              </div>
              
              <div className="result-dates">
                <h4>Date & Time Created</h4>
                <p>{`${item.date_created || 'N/A'} ${item.time_created || ''}`}</p>
                
                <h4>Date & Time Ended</h4>
                <p>{`${item.date_ended || 'N/A'} ${item.time_ended || ''}`}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderRawJson = () => {
    if (!results) {
      return <p>No results to display</p>;
    }

    return (
      <div className="json-container">
        <pre>{JSON.stringify(results, null, 2)}</pre>
        <button 
          className="download-button"
          onClick={() => {
            const dataStr = JSON.stringify(results, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute('href', dataUri);
            downloadAnchorNode.setAttribute('download', 'complaint_analysis.json');
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
          }}
        >
          Download JSON Results
        </button>
      </div>
    );
  };

  const getSentimentColor = (score: number): string => {
    if (score <= 3) return '#ff4d4d'; // Red for negative
    if (score <= 6) return '#ffa64d'; // Orange for neutral
    return '#4caf50'; // Green for positive
  };

  return (
    <div className="analysis-container">
      <div className="header">
        <button className="back-button" onClick={handleBackClick}>
          ← Back to Home
        </button>
        <h1>Sentiment Analysis Results</h1>
      </div>
      
      {isLoading ? (
        <p>Loading analysis results...</p>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : (
        <>
          <div className="tabs">
            <button 
              className={activeTab === 'table' ? 'active' : ''} 
              onClick={() => setActiveTab('table')}
            >
              Table View
            </button>
            <button 
              className={activeTab === 'formatted' ? 'active' : ''} 
              onClick={() => setActiveTab('formatted')}
            >
              Formatted View
            </button>
            <button 
              className={activeTab === 'json' ? 'active' : ''} 
              onClick={() => setActiveTab('json')}
            >
              Raw JSON
            </button>
          </div>
          
          <div className="tab-content">
            {activeTab === 'table' && renderTableView()}
            {activeTab === 'formatted' && renderFormattedView()}
            {activeTab === 'json' && renderRawJson()}
          </div>
        </>
      )}
    </div>
  );
};

export default AnalysisPage;