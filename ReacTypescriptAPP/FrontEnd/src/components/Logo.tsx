import React from 'react';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
}

const Logo: React.FC<LogoProps> = ({ size = 'medium', showText = true }) => {
  const getSizeClass = () => {
    switch (size) {
      case 'small': return 'logo-small';
      case 'large': return 'logo-large';
      default: return 'logo-medium';
    }
  };

  return (
    <div className={`logo ${getSizeClass()}`}>
      <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="40" height="40" rx="8" fill="#C74634"/>
        <path d="M10 20C10 14.4772 14.4772 10 20 10V10C25.5228 10 30 14.4772 30 20V28C30 29.1046 29.1046 30 28 30H12C10.8954 30 10 29.1046 10 28V20Z" fill="white"/>
        <path d="M15 16C15 15.4477 15.4477 15 16 15H24C24.5523 15 25 15.4477 25 16V16C25 16.5523 24.5523 17 24 17H16C15.4477 17 15 16.5523 15 16V16Z" fill="#C74634"/>
        <path d="M15 20C15 19.4477 15.4477 19 16 19H24C24.5523 19 25 19.4477 25 20V20C25 20.5523 24.5523 21 24 21H16C15.4477 21 15 20.5523 15 20V20Z" fill="#C74634"/>
        <path d="M15 24C15 23.4477 15.4477 23 16 23H24C24.5523 23 25 23.4477 25 24V24C25 24.5523 24.5523 25 24 25H16C15.4477 25 15 24.5523 15 24V24Z" fill="#C74634"/>
      </svg>
      
      {showText && (
        <div className="logo-text">
          Chat<span>Classifier</span>
        </div>
      )}
    </div>
  );
};

export default Logo;