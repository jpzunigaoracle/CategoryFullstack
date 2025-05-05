import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import SelfClassAnalysisPage from './pages/SelfClassAnalysisPage';
import VisualizationPage from './pages/VisualizationPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/selfclass-analysis" element={<SelfClassAnalysisPage />} />
          <Route path="/visualization" element={<VisualizationPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;