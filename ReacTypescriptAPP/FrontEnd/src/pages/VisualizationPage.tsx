import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import '../styles/VisualizationPage.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface ComplaintData {
  id: string;
  summary: string;
  sentiment_score: number;
  complaint_type: string;
  date_created: string;
  time_created: string;
  date_ended: string;
  time_ended: string;
}

const VisualizationPage: React.FC = () => {
  const [data, setData] = useState<ComplaintData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('sentiment');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/analyze-complaints/classtype');
        if (response.data && Array.isArray(response.data)) {
          setData(response.data);
        } else if (response.data && response.data.classified_complaints && Array.isArray(response.data.classified_complaints)) {
          setData(response.data.classified_complaints);
        } else {
          throw new Error('Invalid data format received from API');
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load visualization data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleBackClick = () => {
    navigate('/');
  };

  // Calculate average sentiment score
  const calculateAverageSentiment = () => {
    if (data.length === 0) return 0;
    const sum = data.reduce((acc, item) => acc + item.sentiment_score, 0);
    return (sum / data.length).toFixed(2);
  };

  // Group data by complaint type
  const getComplaintTypeCounts = () => {
    const counts: Record<string, number> = {};
    data.forEach(item => {
      const type = item.complaint_type || 'Unclassified';
      counts[type] = (counts[type] || 0) + 1;
    });
    return counts;
  };

  // Group sentiment scores by complaint type
  const getSentimentByComplaintType = () => {
    const sentimentByType: Record<string, number[]> = {};
    data.forEach(item => {
      const type = item.complaint_type || 'Unclassified';
      if (!sentimentByType[type]) {
        sentimentByType[type] = [];
      }
      sentimentByType[type].push(item.sentiment_score);
    });

    // Calculate average for each type
    const result: Record<string, number> = {};
    Object.entries(sentimentByType).forEach(([type, scores]) => {
      const sum = scores.reduce((acc, score) => acc + score, 0);
      result[type] = parseFloat((sum / scores.length).toFixed(2));
    });

    return result;
  };

  // Group data by time of day
  const getDataByTimeOfDay = () => {
    const timeGroups: Record<string, any> = {
      'Morning (6AM-12PM)': { count: 0, sentiment: 0, types: {} },
      'Afternoon (12PM-6PM)': { count: 0, sentiment: 0, types: {} },
      'Evening (6PM-12AM)': { count: 0, sentiment: 0, types: {} },
      'Night (12AM-6AM)': { count: 0, sentiment: 0, types: {} }
    };

    data.forEach(item => {
      if (!item.time_created) return;
      
      // Extract hour from time string (assuming format like "9:30 AM" or "14:30")
      let hour = 0;
      if (item.time_created.includes('AM') || item.time_created.includes('PM')) {
        const timeParts = item.time_created.split(' ')[0].split(':');
        hour = parseInt(timeParts[0]);
        if (item.time_created.includes('PM') && hour !== 12) hour += 12;
        if (item.time_created.includes('AM') && hour === 12) hour = 0;
      } else {
        // 24-hour format
        hour = parseInt(item.time_created.split(':')[0]);
      }

      // Determine time group
      let timeGroup;
      if (hour >= 6 && hour < 12) {
        timeGroup = 'Morning (6AM-12PM)';
      } else if (hour >= 12 && hour < 18) {
        timeGroup = 'Afternoon (12PM-6PM)';
      } else if (hour >= 18 && hour < 24) {
        timeGroup = 'Evening (6PM-12AM)';
      } else {
        timeGroup = 'Night (12AM-6AM)';
      }

      // Update counts and sentiment
      timeGroups[timeGroup].count++;
      timeGroups[timeGroup].sentiment += item.sentiment_score;

      // Update complaint type counts
      const type = item.complaint_type || 'Unclassified';
      timeGroups[timeGroup].types[type] = (timeGroups[timeGroup].types[type] || 0) + 1;
    });

    // Calculate average sentiment for each time group
    Object.keys(timeGroups).forEach(group => {
      if (timeGroups[group].count > 0) {
        timeGroups[group].avgSentiment = parseFloat(
          (timeGroups[group].sentiment / timeGroups[group].count).toFixed(2)
        );
      } else {
        timeGroups[group].avgSentiment = 0;
      }
    });

    return timeGroups;
  };

  // Render sentiment analysis charts
  const renderSentimentCharts = () => {
    const timeData = getDataByTimeOfDay();
    const sentimentByType = getSentimentByComplaintType();
    
    // Data for Sentiment by Time of Day chart
    const sentimentByTimeData = {
      labels: Object.keys(timeData),
      datasets: [
        {
          label: 'Average Sentiment Score',
          data: Object.values(timeData).map(group => group.avgSentiment),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
        },
      ],
    };

    // Data for Sentiment by Complaint Type chart
    const sentimentByTypeData = {
      labels: Object.keys(sentimentByType),
      datasets: [
        {
          label: 'Average Sentiment Score',
          data: Object.values(sentimentByType),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    return (
      <>
        <div className="charts-container">
          <div className="stat-card">
            <h3>Average Sentiment Score</h3>
            <div className="big-number">{calculateAverageSentiment()}</div>
            <p>out of 10</p>
          </div>

          <div className="chart-card">
            <h3>Sentiment Score by Time of Day</h3>
            <div style={{ height: '250px' }}>
              <Bar 
                data={sentimentByTimeData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 10,
                      title: {
                        display: true,
                        text: 'Average Sentiment Score'
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>

        <div className="full-width-charts">
          <div className="chart-card">
            <h3>Sentiment Score by Complaint Type</h3>
            <div style={{ height: '250px' }}>
              <Bar 
                data={sentimentByTypeData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 10,
                      title: {
                        display: true,
                        text: 'Average Sentiment Score'
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      </>
    );
  };

  // Render complaint type statistics charts
  const renderComplaintTypeCharts = () => {
    const typeCounts = getComplaintTypeCounts();
    const timeData = getDataByTimeOfDay();
    
    // Data for Complaint Type Distribution chart
    const typeDistributionData = {
      labels: Object.keys(typeCounts),
      datasets: [
        {
          label: 'Number of Complaints',
          data: Object.values(typeCounts),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    // Prepare data for Complaint Type by Time of Day chart
    const complaintTypesByTime = {
      labels: Object.keys(timeData),
      datasets: Object.keys(typeCounts).map((type, index) => {
        const colors = [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)',
        ];
        
        return {
          label: type,
          data: Object.values(timeData).map(group => group.types[type] || 0),
          backgroundColor: colors[index % colors.length],
          borderColor: colors[index % colors.length].replace('0.5', '1'),
          borderWidth: 1,
        };
      }),
    };

    return (
      <>
        <div className="complaint-charts-container">
          <div className="stat-card">
            <h3>Total Complaints</h3>
            <div className="big-number">{data.length}</div>
            <p>complaints analyzed</p>
          </div>

          <div className="chart-card">
            <h3>Complaint Type Distribution</h3>
            <div style={{ height: '250px' }}>
              <Pie 
                data={typeDistributionData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'right',
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>

        <div className="full-width-charts">
          <div className="chart-card">
            <h3>Complaint Types by Time of Day</h3>
            <div style={{ height: '250px' }}>
              <Bar 
                data={complaintTypesByTime} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    x: {
                      stacked: true,
                    },
                    y: {
                      stacked: true,
                      title: {
                        display: true,
                        text: 'Number of Complaints'
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="visualization-container">
      <div className="header">
        <button className="back-button" onClick={handleBackClick}>
          ← Back to Home
        </button>
        <h1>Customer Complaint Analytics</h1>
      </div>
      
      {isLoading ? (
        <div className="loading">Loading visualization data...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="tabs">
            <button 
              className={activeTab === 'sentiment' ? 'active' : ''} 
              onClick={() => setActiveTab('sentiment')}
            >
              Sentiment Analysis
            </button>
            <button 
              className={activeTab === 'complaint-types' ? 'active' : ''} 
              onClick={() => setActiveTab('complaint-types')}
            >
              Complaint Type Statistics
            </button>
          </div>
          
          <div className="tab-content">
            {activeTab === 'sentiment' && renderSentimentCharts()}
            {activeTab === 'complaint-types' && renderComplaintTypeCharts()}
          </div>
        </>
      )}
    </div>
  );
};

export default VisualizationPage;