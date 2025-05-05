import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import SelfClassAnalysisPage from './pages/SelfClassAnalysisPage';
import VisualizationPage from './pages/VisualizationPage';
import Logo from './components/Logo';
import OCIPoweredBadge from './components/OCIPoweredBadge';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="container navbar-content">
            <Link to="/" className="logo">
              <Logo />
            </Link>
            <OCIPoweredBadge />
          </div>
        </nav>
        
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/selfclass-analysis" element={<SelfClassAnalysisPage />} />
            <Route path="/visualization" element={<VisualizationPage />} />
          </Routes>
        </main>
        
        <footer className="footer">
          <div className="container footer-content">
            <div>© {new Date().getFullYear()} Chat-Classifier</div>
            {/* Remove the OCIPoweredBadge from the footer */}
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;