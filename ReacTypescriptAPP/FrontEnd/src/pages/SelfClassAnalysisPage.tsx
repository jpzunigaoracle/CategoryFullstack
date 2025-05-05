import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AnalysisPage.css';

interface ComplaintItem {
  id: number;
  summary: string;
  sentiment_score: number;
  date_created: string;
  time_created: string;
  date_ended: string;
  time_ended: string;
  original_dialog: string;
  complaint_type: string;
}

interface ClassificationData {
  categories: string[];
  classified_complaints: ComplaintItem[];
}

const SelfClassAnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('table');
  const [results, setResults] = useState<ComplaintItem[] | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Try to get results from localStorage
    const storedResults = localStorage.getItem('selfClassResults');
    const storedCategories = localStorage.getItem('complaintCategories');
    
    if (storedResults) {
      try {
        // Parse the stored results
        const parsedData = JSON.parse(storedResults);
        
        // Check if the data is already in the expected format (array of complaints)
        if (Array.isArray(parsedData)) {
          setResults(parsedData);
        } 
        // Check if the data has the classified_complaints property
        else if (parsedData && parsedData.classified_complaints && Array.isArray(parsedData.classified_complaints)) {
          setResults(parsedData.classified_complaints);
          
          if (parsedData.categories && Array.isArray(parsedData.categories)) {
            setCategories(parsedData.categories);
          }
        } else {
          throw new Error('Unexpected data format');
        }
        
        // If we have stored categories separately
        if (storedCategories) {
          try {
            const parsedCategories = JSON.parse(storedCategories);
            if (Array.isArray(parsedCategories)) {
              setCategories(parsedCategories);
            }
          } catch (err) {
            console.error('Error parsing stored categories:', err);
          }
        }
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
    if (!results || results.length === 0) {
      return <p>No results to display</p>;
    }

    return (
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Summary</th>
              <th>Complaint Type</th>
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
                <td>{item.complaint_type || 'Unclassified'}</td>
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
    if (!results || results.length === 0) {
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
                
                <h4>Complaint Type</h4>
                <p className="complaint-type">{item.complaint_type || 'Unclassified'}</p>
                
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
                
                {item.original_dialog && (
                  <>
                    <h4>Original Dialog</h4>
                    <div className="dialog-content" dangerouslySetInnerHTML={{ __html: item.original_dialog }}></div>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCategoriesView = () => {
    if (!categories || categories.length === 0 || !results || results.length === 0) {
      return <p>No categories to display</p>;
    }

    // Count complaints by category
    const categoryCounts: Record<string, number> = {};
    categories.forEach(category => {
      categoryCounts[category] = 0;
    });
    
    results.forEach(complaint => {
      if (complaint.complaint_type in categoryCounts) {
        categoryCounts[complaint.complaint_type]++;
      }
    });

    return (
      <div className="categories-container">
        <h3>Complaint Categories</h3>
        <div className="category-list">
          {categories.map(category => (
            <div key={category} className="category-item">
              <h4>{category}</h4>
              <p>{categoryCounts[category]} complaints</p>
              <div className="category-bar-container">
                <div 
                  className="category-bar" 
                  style={{ 
                    width: `${(categoryCounts[category] / results.length) * 100}%`,
                    backgroundColor: getCategoryColor(category)
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderRawJson = () => {
    if (!results) {
      return <p>No results to display</p>;
    }

    const fullData = categories.length > 0 
      ? { categories, classified_complaints: results } 
      : results;

    return (
      <div className="json-container">
        <pre>{JSON.stringify(fullData, null, 2)}</pre>
        <button 
          className="download-button"
          onClick={() => {
            const dataStr = JSON.stringify(fullData, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute('href', dataUri);
            downloadAnchorNode.setAttribute('download', 'complaint_classification.json');
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

  const getCategoryColor = (category: string): string => {
    // Generate a consistent color based on the category string
    let hash = 0;
    for (let i = 0; i < category.length; i++) {
      hash = category.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Convert to RGB color
    const r = (hash & 0xFF0000) >> 16;
    const g = (hash & 0x00FF00) >> 8;
    const b = hash & 0x0000FF;
    
    return `rgb(${r}, ${g}, ${b})`;
  };

  return (
    <div className="analysis-container">
      <div className="header">
        <button className="back-button" onClick={handleBackClick}>
          ← Back to Home
        </button>
        <h1>Self-Classification Analysis Results</h1>
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
              className={activeTab === 'categories' ? 'active' : ''} 
              onClick={() => setActiveTab('categories')}
            >
              Categories
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
            {activeTab === 'categories' && renderCategoriesView()}
            {activeTab === 'json' && renderRawJson()}
          </div>
        </>
      )}
    </div>
  );
};

export default SelfClassAnalysisPage;