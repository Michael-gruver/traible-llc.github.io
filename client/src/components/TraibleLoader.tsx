import React, { useEffect, useState } from 'react';

// Interface for component props
interface TraibleLoaderProps {
  // Core functionality
  size?: 'small' | 'medium' | 'large';
  showProgress?: boolean;
  initialProgress?: number;
  showLogo?: boolean;
  autoIncrease?: boolean;
  duration?: number; // Duration in seconds
  increaseBy?: number; // New prop to increase progress by specific percentage
  
  // Text customization
  showText?: boolean;
  customMessages?: {
    initial?: string;
    middle?: string;
    final?: string;
    complete?: string;
  };
  
  // Visual customization
  showFileIcons?: boolean;
  showAnimatedDots?: boolean;
  showTimeRemaining?: boolean;
  
  // Container styling
  className?: string;
  centerInParent?: boolean;
}

const TraibleLoader: React.FC<TraibleLoaderProps> = ({
  // Default values for props
  size = 'medium',
  showProgress = true,
  initialProgress = 0,
  autoIncrease = true,
  duration = 0, // 0 means no time limit (original behavior)
  increaseBy = 0, // New prop with default value of 0 (no increase)
  showLogo= false,
  showText = true,
  customMessages = {
    initial: "Analyzing Files",
    middle: "Processing Data",
    final: "Finalizing Analysis", 
    complete: "Ready to View"
  },
  
  showFileIcons = true,
  showAnimatedDots = true,
  showTimeRemaining = false,
  
  className = '',
  centerInParent = true
}) => {
  const [progress, setProgress] = useState(initialProgress);
  const [animationStep, setAnimationStep] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(duration);
  
  // Size mapping
  const sizeMap = {
    small: {
      container: 'h-32',
      loader: 'w-16 h-16',
      loaderInner: 'w-12 h-12',
      icon: 'w-8 h-8',
      fileIcon: 'w-6 h-6',
      progressBar: 'w-48 h-2',
      textPrimary: 'text-sm',
      textSecondary: 'text-xs',
    },
    medium: {
      container: 'h-64',
      loader: 'w-24 h-24',
      loaderInner: 'w-20 h-20',
      icon: 'w-10 h-10',
      fileIcon: 'w-8 h-8',
      progressBar: 'w-64 h-3',
      textPrimary: 'text-lg',
      textSecondary: 'text-sm',
    },
    large: {
      container: 'h-80',
      loader: 'w-32 h-32',
      loaderInner: 'w-24 h-24',
      icon: 'w-12 h-12',
      fileIcon: 'w-10 h-10',
      progressBar: 'w-80 h-4',
      textPrimary: 'text-xl',
      textSecondary: 'text-base',
    }
  };
  
  const sizes = sizeMap[size];
  
  // Handle progress increase from increaseBy prop
  useEffect(() => {
    if (increaseBy > 0) {
      setProgress(prev => {
        const newProgress = Math.min(100, prev + increaseBy);
        return newProgress;
      });
    }
  }, [increaseBy]);
  
  // Auto-increase progress
  useEffect(() => {
    if (!autoIncrease) return;
    
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        
        // If duration is set, calculate progress based on time
        if (duration > 0) {
          return Math.min(100, (duration - timeRemaining) / duration * 100);
        }
        
        // Original behavior: increment by 1
        return prev + 1;
      });
      
      // Handle time remaining if duration is set
      if (duration > 0) {
        setTimeRemaining(prev => {
          if (prev <= 0) {
            clearInterval(progressInterval);
            return 0;
          }
          return prev - 0.1;
        });
      }
    }, duration > 0 ? 100 : 30); // Faster updates for timed version
    
    return () => clearInterval(progressInterval);
  }, [autoIncrease, duration, timeRemaining]);
  
  // Animated dots effect
  useEffect(() => {
    if (!showAnimatedDots) return;
    
    const stepInterval = setInterval(() => {
      setAnimationStep(prev => (prev + 1) % 3);
    }, 800);
    
    return () => clearInterval(stepInterval);
  }, [showAnimatedDots]);
  
  // Determine current message based on progress
  const getCurrentMessage = () => {
    if (progress < 33) return customMessages.initial;
    if (progress < 66) return customMessages.middle;
    if (progress < 100) return customMessages.final;
    return customMessages.complete;
  };
  
  // Format time remaining
  const formatTimeRemaining = () => {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = Math.floor(timeRemaining % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };
  
  // Container classes
  const containerClasses = `flex flex-col items-center justify-center w-full ${sizes.container} p-8 ${className} ${centerInParent ? 'absolute inset-0 m-auto' : ''}`;
  
  // Calculate rotation for orbiting elements
  const getOrbitStyle = (duration: number, reverse = false) => ({
    animation: `spin ${duration}s linear infinite ${reverse ? 'reverse' : ''}`,
    transformOrigin: "center"
  });
  
  return (
    <div className={containerClasses}>
      {/* Main loader container */}
      
    { showLogo && <div className="relative w-32 h-32 mb-6">
        {/* Central loader ring */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={`${sizes.loader} rounded-full border-4 border-black bg-white flex items-center justify-center`} style={{ boxShadow: '0 0 20px rgba(136, 160, 194, 0.5)' }}>
            <div className={`${sizes.loaderInner} rounded-full bg-white border-2 flex items-center justify-center`} style={{ borderColor: 'rgba(136, 160, 194, 0.7)' }}>
              {/* Traible logo/icon - using document icon as placeholder */}
              <svg className={`${sizes.icon} text-black`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
        
        {/* Orbiting File Icons - Only shown if showFileIcons is true */}
        {showFileIcons && (
          <>
            <div className="absolute inset-0" style={getOrbitStyle(8)}>
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-4">
                <div className={`${sizes.fileIcon} rounded-full flex items-center justify-center bg-white text-black border-2`} style={{ borderColor: 'rgba(136, 160, 194, 0.7)' }}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="absolute inset-0" style={getOrbitStyle(8, true)}>
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-4">
                <div className={`${sizes.fileIcon} rounded-full flex items-center justify-center bg-white text-black border-2`} style={{ borderColor: 'rgba(136, 160, 194, 0.7)' }}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="absolute inset-0" style={getOrbitStyle(6)}>
              <div className="absolute top-1/2 left-0 transform -translate-y-1/2 -translate-x-4">
                <div className={`${sizes.fileIcon} rounded-full flex items-center justify-center bg-white text-black border-2`} style={{ borderColor: 'rgba(136, 160, 194, 0.7)' }}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="absolute inset-0" style={getOrbitStyle(6, true)}>
              <div className="absolute top-1/2 right-0 transform -translate-y-1/2 translate-x-4">
                <div className={`${sizes.fileIcon} rounded-full flex items-center justify-center bg-white text-black border-2`} style={{ borderColor: 'rgba(136, 160, 194, 0.7)' }}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </div>
              </div>
            </div>
          </>
        )}
      </div>}
      
      {/* Progress Bar - Only shown if showProgress is true */}
      {showProgress && (
        <div className={`${sizes.progressBar} bg-gray-200 border-2 border-white rounded-full overflow-hidden mb-3`}>
          <div 
            className="h-full transition-all ease-out duration-300"
            style={{ 
              width: `${progress}%`,
              background: `linear-gradient(to right, #000000, rgba(136, 160, 194, 0.7), #000000)`
            }}
          />
        </div>
      )}
      
      {/* Processing Text - Only shown if showText is true */}
      {showText && (
        <div className={`${sizes.textPrimary} font-medium text-white  mb-1`}>
          {getCurrentMessage()}
        </div>
      )}
      
      {/* Time Remaining - Only shown if duration > 0 and showTimeRemaining is true */}
      {duration > 0 && showTimeRemaining && (
        <div className={`${sizes.textSecondary} text-white  mb-2`}>
          Time remaining: {formatTimeRemaining()}
        </div>
      )}
      
      {/* Animated Dots - Only shown if showAnimatedDots and showText are true */}
      {showText && showAnimatedDots && (
        <div className={`${sizes.textSecondary} text-white flex items-center`}>
          <span>Traible{animationStep === 0 ? '.' : animationStep === 1 ? '..' : '...'}</span>
        </div>
      )}
    </div>
  );
};

export default TraibleLoader;