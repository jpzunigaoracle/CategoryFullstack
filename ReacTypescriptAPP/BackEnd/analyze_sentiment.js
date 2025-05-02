const { PythonShell } = require('python-shell');
const path = require('path');

/**
 * Analyzes text for sentiment using Python script
 * @param {string} text - The text to analyze
 * @param {string} modelName - The model name to use
 * @returns {Promise<Array>} - Promise resolving to sentiment analysis results
 */
function analyzeSentiment(text, modelName) {
  return new Promise((resolve, reject) => {
    // Create options for Python script
    const options = {
      mode: 'text',
      pythonPath: 'python', // or 'python3' depending on your environment
      pythonOptions: ['-u'], // unbuffered output
      scriptPath: path.join(__dirname),
      args: [
        '--text', text,
        '--model_name', modelName
        // No longer passing prompt_template - Python will handle this
      ]
    };

    // Run the Python script
    PythonShell.run('analyze_sentiment.py', options, (err, results) => {
      if (err) {
        console.error('Error running Python script:', err);
        return reject(err);
      }
      
      try {
        // The last line of output should be our JSON result
        const jsonOutput = results[results.length - 1];
        const analysisResults = JSON.parse(jsonOutput);
        resolve(analysisResults);
      } catch (error) {
        console.error('Error parsing Python script output:', error);
        reject(error);
      }
    });
  });
}

module.exports = { analyzeSentiment };