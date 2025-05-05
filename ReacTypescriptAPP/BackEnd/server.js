const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { PythonShell } = require('python-shell');
const multer = require('multer');
require('dotenv').config(); // Load environment variables from .env file
const app = express();
const PORT = process.env.PORT || 5000;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: function(req, file, cb) {
    cb(null, 'uploaded-complaints.json');
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: function(req, file, cb) {
    // Accept only JSON files
    if (file.mimetype !== 'application/json') {
      return cb(new Error('Only JSON files are allowed'));
    }
    cb(null, true);
  },
  limits: {
    fileSize: 1024 * 1024 // Limit file size to 1MB
  }
});

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

// Middleware
app.use(cors());
app.use(express.json());

// Root route
app.get('/', (req, res) => {
  res.send('SMEG Sentiment Analysis API is running. Use /api/complaints, /api/analyze-complaints, /api/upload/complaints, or /api/upload/analyze-complaints endpoints.');
});

// Function to read JSONBin.io credentials
function getBinCredentials() {
  try {
    const binDataPath = path.join(__dirname, 'binio', 'BinData.txt');
    const data = fs.readFileSync(binDataPath, 'utf8').split('\n');
    return {
      apiKey: data[1].trim(),
      binId: data[3].trim()
    };
  } catch (error) {
    console.error('Error reading bin credentials:', error);
    return { apiKey: null, binId: null };
  }
}

// Path to the local ComplainsList.json file (as fallback)
const complaintsFilePath = path.join(__dirname, 'ComplainsList.json');

// Endpoint to get complaints data (now from JSONBin.io)
app.get('/api/complaints', async (req, res) => {
  try {
    const { apiKey, binId } = getBinCredentials();
    
    if (!apiKey || !binId) {
      throw new Error('Missing JSONBin.io credentials');
    }
    
    // Fetch data from JSONBin.io
    const response = await axios.get(`https://api.jsonbin.io/v3/b/${binId}`, {
      headers: {
        'X-Master-Key': apiKey,
        'X-Bin-Meta': 'false'
      }
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching from JSONBin.io:', error);
    
    // Fallback to local file
    console.log('Falling back to local file...');
    try {
      if (fs.existsSync(complaintsFilePath)) {
        const complaintsData = JSON.parse(fs.readFileSync(complaintsFilePath, 'utf8'));
        res.json(complaintsData);
      } else {
        res.status(404).json({ error: 'Complaints file not found' });
      }
    } catch (fallbackError) {
      console.error('Error reading local complaints file:', fallbackError);
      res.status(500).json({ error: 'Failed to read complaints data' });
    }
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

// New endpoint to handle uploaded complaints file
app.post('/api/upload/complaints', upload.single('complaintsFile'), (req, res) => {
  try {
    if (!req.file) {
      throw new Error('No file uploaded');
    }
    
    // Read the uploaded file
    const uploadedFilePath = path.join(uploadsDir, 'uploaded-complaints.json');
    const complaintsData = JSON.parse(fs.readFileSync(uploadedFilePath, 'utf8'));
    
    // Return the complaints data
    res.json(complaintsData);
  } catch (error) {
    console.error('Error processing uploaded file:', error);
    
    // Fallback to local file
    console.log('Falling back to local file...');
    try {
      if (fs.existsSync(complaintsFilePath)) {
        const complaintsData = JSON.parse(fs.readFileSync(complaintsFilePath, 'utf8'));
        res.json(complaintsData);
      } else {
        res.status(404).json({ error: 'Complaints file not found' });
      }
    } catch (fallbackError) {
      console.error('Error reading local complaints file:', fallbackError);
      res.status(500).json({ error: 'Failed to read complaints data' });
    }
  }
});

// New endpoint to analyze uploaded complaints file
app.post('/api/upload/analyze-complaints', upload.single('complaintsFile'), (req, res) => {
  try {
    if (!req.file) {
      throw new Error('No file uploaded');
    }
    
    const uploadedFilePath = path.join(uploadsDir, 'uploaded-complaints.json');
    const pythonScriptPath = path.join(__dirname, 'analyze_complaints.py');
    
    // Check if the Python script exists
    if (!fs.existsSync(pythonScriptPath)) {
      return res.status(404).json({ error: 'Analysis script not found' });
    }
    
    // Create a temporary copy of the uploaded file with the expected name
    const tempFilePath = path.join(__dirname, 'temp-complaints.json');
    fs.copyFileSync(uploadedFilePath, tempFilePath);
    
    // Create options for Python script with the uploaded file path
    const options = {
      mode: 'text',
      pythonPath: 'python', // or 'python3' depending on your environment
      pythonOptions: ['-u'], // unbuffered output
      scriptPath: path.dirname(pythonScriptPath),
      args: ['--file', tempFilePath]
    };
    
    // Run the Python script with the uploaded file
    PythonShell.run('analyze_complaints.py', options)
      .then(results => {
        try {
          // Clean up the temporary file
          if (fs.existsSync(tempFilePath)) {
            fs.unlinkSync(tempFilePath);
          }
          
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
        
        // Clean up the temporary file if it exists
        if (fs.existsSync(tempFilePath)) {
          fs.unlinkSync(tempFilePath);
        }
        
        // Fallback to analyzing the local file
        console.log('Falling back to local file analysis...');
        const fallbackOptions = {
          mode: 'text',
          pythonPath: 'python',
          pythonOptions: ['-u'],
          scriptPath: path.dirname(pythonScriptPath),
          args: []
        };
        
        PythonShell.run('analyze_complaints.py', fallbackOptions)
          .then(fallbackResults => {
            try {
              const jsonOutput = fallbackResults[fallbackResults.length - 1];
              const analysisResults = JSON.parse(jsonOutput);
              res.json(analysisResults);
            } catch (error) {
              res.status(500).json({ 
                error: 'Failed to analyze complaints with fallback',
                details: error.message
              });
            }
          })
          .catch(fallbackErr => {
            res.status(500).json({ 
              error: 'Failed to analyze complaints with fallback',
              details: fallbackErr.message
            });
          });
      });
  } catch (error) {
    console.error('Error processing uploaded file:', error);
    res.status(500).json({ error: 'Failed to process uploaded file' });
  }
});

// New endpoint to classify complaints into categories
app.get('/api/analyze-complaints/classtype', (req, res) => {
  const pythonScriptPath = path.join(__dirname, 'analyze_complaints_secondstage.py');
  
  // Check if the Python script exists
  if (!fs.existsSync(pythonScriptPath)) {
    return res.status(404).json({ error: 'Classification script not found' });
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
  PythonShell.run('analyze_complaints_secondstage.py', options)
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
          error: 'Failed to parse classification results',
          details: error.message,
          output: results
        });
      }
    })
    .catch(err => {
      console.error('Error running Python script:', err);
      res.status(500).json({ 
        error: 'Failed to classify complaints',
        details: err.message
      });
    });
});

// Start the server
app.listen(PORT, () => {
  // After the server starts and you're printing the endpoints
  console.log('Server running on port 5000');
  console.log('API endpoints:');
  console.log('- GET /api/complaints: Get raw complaints data');
  console.log('- GET /api/analyze-complaints: Get sentiment analysis report');
  console.log('- GET /api/analyze-complaints/classtype: Get self classified complaints');
});