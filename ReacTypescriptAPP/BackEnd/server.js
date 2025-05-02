const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { PythonShell } = require('python-shell');
require('dotenv').config(); // Load environment variables from .env file
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Root route
app.get('/', (req, res) => {
  res.send('SMEG Sentiment Analysis API is running. Use /api/complaints or /api/analyze-complaints endpoints.');
});

// Path to the ComplainsList.json file
const complaintsFilePath = path.join(__dirname, 'ComplainsList.json');

// Endpoint to get raw complaints data
app.get('/api/complaints', (req, res) => {
  try {
    if (fs.existsSync(complaintsFilePath)) {
      const complaintsData = JSON.parse(fs.readFileSync(complaintsFilePath, 'utf8'));
      res.json(complaintsData);
    } else {
      res.status(404).json({ error: 'Complaints file not found' });
    }
  } catch (error) {
    console.error('Error reading complaints file:', error);
    res.status(500).json({ error: 'Failed to read complaints data' });
  }
});

// Endpoint to analyze complaints using Python script
app.get('/api/analyze-complaints', (req, res) => {
  const pythonScriptPath = path.join(__dirname, 'analyze_complaints.py');
  
  // Check if the Python script exists
  if (!fs.existsSync(pythonScriptPath)) {
    return res.status(404).json({ error: 'Analysis script not found' });
  }
  
  // Create options for Python script
  const options = {
    mode: 'text',
    pythonPath: 'python', // or 'python3' depending on your environment
    pythonOptions: ['-u'], // unbuffered output
    scriptPath: path.dirname(pythonScriptPath),
    args: []
  };
  
  // Run the Python script with improved error handling
  PythonShell.run('analyze_complaints.py', options)
    .then(results => {
      try {
        // The last line of output should be our JSON result
        const jsonOutput = results[results.length - 1];
        const analysisResults = JSON.parse(jsonOutput);
        
        // Return the exact format needed
        res.json(analysisResults);
      } catch (error) {
        console.error('Error parsing Python script output:', error);
        console.error('Python output:', results);
        res.status(500).json({ 
          error: 'Failed to parse analysis results',
          details: error.message,
          output: results
        });
      }
    })
    .catch(err => {
      console.error('Error running Python script:', err);
      res.status(500).json({ 
        error: 'Failed to analyze complaints',
        details: err.message
      });
    });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API endpoints:`);
  console.log(`- GET /api/complaints: Get raw complaints data`);
  console.log(`- GET /api/analyze-complaints: Get sentiment analysis report`);
});