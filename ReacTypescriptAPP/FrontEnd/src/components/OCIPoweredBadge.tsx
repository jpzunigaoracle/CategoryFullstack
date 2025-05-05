import React from 'react';
import '../styles/OCIPoweredBadge.css';

interface OCIPoweredBadgeProps {
  size?: 'small' | 'medium' | 'large';
}

const OCIPoweredBadge: React.FC<OCIPoweredBadgeProps> = ({ size = 'medium' }) => {
  return (
    <a 
      href="https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/" 
      target="_blank" 
      rel="noopener noreferrer"
      className={`oci-powered-badge oci-badge-${size}`}
    >
      <img 
        src="/oracle-logo.png" 
        alt="Oracle" 
        className="oracle-main-logo"
        onError={(e) => {
          e.currentTarget.onerror = null;
          e.currentTarget.src = 'https://www.oracle.com/a/ocom/img/oracle-logo.svg';
        }}
      />
      <div className="oci-text-container">
        <span className="powered-by-text">Powered by</span>
        <span className="oci-text">OCI Generative AI</span>
      </div>
    </a>
  );
};

export default OCIPoweredBadge;