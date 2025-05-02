const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const fs = require('fs');

module.exports = function(app) {
  // Create an API endpoint to serve the ComplainsList.json file
  app.get('/api/complaints', (req, res) => {
    const jsonPath = path.resolve(__dirname, '../../BackEnd/ComplainsList.json');
    
    try {
      const jsonData = fs.readFileSync(jsonPath, 'utf8');
      const data = JSON.parse(jsonData);
      res.json(data);
    } catch (error) {
      console.error('Error reading complaints data:', error);
      res.status(500).json({ error: 'Failed to load complaints data' });
    }
  });
};