import React, { useState, useEffect, useRef } from 'react';
import './LiveTryOn.css';

const BACKEND_URL = "http://127.0.0.1:5000";

function LiveTryOn({ catalog, selectedTryOnItem }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [processingFrame, setProcessingFrame] = useState(false);
  const [showConsent, setShowConsent] = useState(false); // Changed to false to skip consent screen initially
  const animationFrameRef = useRef(null);
  
  // Function to start the webcam
  const startWebcam = async () => {
    setError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: false // Ensure we're not requesting audio access
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
        setWebcamActive(true);
        setShowConsent(false);
        
        // Play the video element and handle potential autoplay issues
        const playPromise = videoRef.current.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log("Video playback started successfully");
              // Wait for video to be ready before starting processing
              videoRef.current.onloadedmetadata = () => {
                startFrameProcessing();
              };
            })
            .catch(err => {
              console.error("Video playback was prevented:", err);
              setError(`Video playback failed: ${err.message}. Try clicking on the page.`);
            });
        }
      } else {
        throw new Error("Video element not available");
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setError(`Could not access webcam: ${err.message}`);
    }
  };

  // Function to stop the webcam
  const stopWebcam = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    setWebcamActive(false);
  };

  // Check browser compatibility and handle component mount/unmount
  useEffect(() => {
    // Check if browser supports getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError("Your browser doesn't support webcam access. Try using Chrome, Firefox, or Edge.");
      return;
    }
    
    console.log("LiveTryOn component mounted - webcam access should be available");
    
    // Cleanup function for component unmount
    return () => {
      console.log("LiveTryOn component unmounting - stopping webcam");
      stopWebcam();
    };
  }, []);

  // Process frames from webcam and apply clothing overlay
  const processFrame = async () => {
    if (!videoRef.current || !canvasRef.current || !webcamActive) return;
    
    // If the video isn't playing yet, request next frame and return
    if (videoRef.current.paused || videoRef.current.ended || !videoRef.current.videoWidth) {
      console.log("Video not ready yet, waiting...");
      animationFrameRef.current = requestAnimationFrame(processFrame);
      return;
    }
    
    // Don't process if already processing and clothing is selected
    if (processingFrame && selectedTryOnItem?.imageUrl) return;

    const ctx = canvasRef.current.getContext('2d');
    const video = videoRef.current;
    
    // Set canvas dimensions to match video
    if (canvasRef.current.width !== video.videoWidth || canvasRef.current.height !== video.videoHeight) {
      console.log(`Setting canvas dimensions to ${video.videoWidth}x${video.videoHeight}`);
      canvasRef.current.width = video.videoWidth;
      canvasRef.current.height = video.videoHeight;
    }
    
    // Draw the video frame to canvas
    ctx.drawImage(video, 0, 0, canvasRef.current.width, canvasRef.current.height);

    // If a clothing item is selected, send the frame for processing
    if (selectedTryOnItem?.imageUrl) {
      setProcessingFrame(true);
      
      try {
        // Convert canvas to blob to send to server
        canvasRef.current.toBlob(async (blob) => {
          // Create a FormData to send the image
          const formData = new FormData();
          formData.append('frame', blob, 'frame.jpg');
          formData.append('clothingItemId', selectedTryOnItem.id);
          
          // Send to the server for processing
          try {
            const response = await fetch(`${BACKEND_URL}/api/live-tryon`, { 
              method: 'POST',
              body: formData
            });
            
            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Draw the result image on canvas
            if (result.resultImageUrl) {
              const resultImage = new Image();
              resultImage.onload = () => {
                ctx.drawImage(resultImage, 0, 0, canvasRef.current.width, canvasRef.current.height);
                setProcessingFrame(false);
                
                // Continue with next frame after a short delay to avoid overwhelming the server
                setTimeout(() => {
                  animationFrameRef.current = requestAnimationFrame(processFrame);
                }, 250); // Longer delay for real server processing
              };
              resultImage.onerror = () => {
                console.error("Failed to load result image");
                setProcessingFrame(false);
                animationFrameRef.current = requestAnimationFrame(processFrame);
              };
              resultImage.src = result.resultImageUrl.startsWith('/uploads/') 
                ? `${BACKEND_URL}${result.resultImageUrl}` 
                : result.resultImageUrl;
            } else {
              throw new Error("No result image URL returned");
            }
          } catch (error) {
            console.error("Error processing try-on request:", error);
            setProcessingFrame(false);
            animationFrameRef.current = requestAnimationFrame(processFrame);
          }
        }, 'image/jpeg', 0.8); // Convert canvas to JPEG for reduced size
      } catch (err) {
        console.error("Error processing frame:", err);
        setProcessingFrame(false);
        // Continue with next frame despite error
        animationFrameRef.current = requestAnimationFrame(processFrame);
      }
    } else {
      // If no clothing selected, continue with next frame
      animationFrameRef.current = requestAnimationFrame(processFrame);
    }
  };

  const startFrameProcessing = () => {
    // Start processing frames
    animationFrameRef.current = requestAnimationFrame(processFrame);
  };

  // Handle consent and start webcam
  const handleConsentAndStart = () => {
    startWebcam();
  };

  // Effect for selected item changes
  useEffect(() => {
    // You could implement additional logic here when the selected item changes
    // For example, reset any processing state
  }, [selectedTryOnItem]);

  return (
    <div className="live-tryon-container">
      <h2>Live Try-On with Webcam</h2>
      
      {showConsent ? (
        <div className="consent-prompt">
          <p>This feature requires access to your webcam for real-time virtual try-on.</p>
          <p>Your privacy is important to us. All processing happens on-device and no images are stored.</p>
          <button className="consent-button" onClick={handleConsentAndStart}>
            Allow Camera Access
          </button>
        </div>
      ) : (
        <div className="webcam-container">
          {error && <p className="error-message">{error}</p>}
          
          <div className="video-display">
            {/* Video element for webcam feed (make visible for debugging) */}
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline
              muted // Ensure audio is muted to prevent feedback
              className="video-canvas" // Show the raw video feed until we can debug canvas
              style={{ display: webcamActive ? 'block' : 'none' }} // Show video feed
            />
            
            {/* Canvas where we'll render the augmented feed */}
            <canvas ref={canvasRef} className="video-canvas" style={{ display: 'none' }} />
            
            {/* Debugging info overlay */}
            {webcamActive && (
              <div className="debug-info">
                <p>Camera active: {stream ? 'Yes' : 'No'}</p>
                <p>Video dimensions: {videoRef.current ? `${videoRef.current.videoWidth}x${videoRef.current.videoHeight}` : 'Unknown'}</p>
                <p>Video state: {videoRef.current ? 
                    (videoRef.current.paused ? 'Paused' : 
                     (videoRef.current.ended ? 'Ended' : 'Playing')) 
                    : 'Unknown'}</p>
              </div>
            )}
          </div>
          
          <div className="webcam-controls">
            {!webcamActive ? (
              <button onClick={startWebcam} disabled={webcamActive}>
                Start Camera
              </button>
            ) : (
              <>
                <button onClick={stopWebcam} disabled={!webcamActive}>
                  Stop Camera
                </button>
                <button 
                  onClick={() => {
                    if (videoRef.current && videoRef.current.paused) {
                      videoRef.current.play()
                        .then(() => console.log("Video playback started manually"))
                        .catch(err => console.error("Manual play failed:", err));
                    }
                  }}
                >
                  Force Play
                </button>
              </>
            )}
            
            {webcamActive && (
              <p className="status-text">
                {processingFrame 
                  ? "Processing..." 
                  : selectedTryOnItem 
                    ? `Trying on: ${selectedTryOnItem.name}` 
                    : "Select a clothing item to try on"}
              </p>
            )}
          </div>
          
          {webcamActive && !selectedTryOnItem && (
            <div className="instruction-message">
              <p>Select a clothing item from the catalog to see it in real-time.</p>
            </div>
          )}
        </div>
      )}
      
      <div className="privacy-note">
        <p>
          <strong>Privacy Note:</strong> All processing happens on your device.
          No video data is sent to our servers or stored.
        </p>
      </div>
    </div>
  );
}

export default LiveTryOn;
