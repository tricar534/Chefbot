import React, { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Dynamic backend URL detection - works in Codespaces and local
  const getBackendUrl = () => {
    // 1. Check for environment variable first (highest priority)
    if (import.meta.env.VITE_BACKEND_URL) {
      return import.meta.env.VITE_BACKEND_URL;
    }
    
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    const port = window.location.port;
    
    // 2. Detect GitHub Codespaces
    if (hostname.includes('app.github.dev')) {
      // Codespaces URL format: https://CODESPACE-NAME-PORT.app.github.dev
      // Frontend: https://CODESPACE-NAME-5173.app.github.dev
      // Backend:  https://CODESPACE-NAME-5000.app.github.dev
      
      // Replace the port number in the hostname
      const backendHostname = hostname.replace(/-\d+\.app\.github\.dev$/, '-5000.app.github.dev');
      return `https://${backendHostname}`;
    }
    
    // 3. Detect preview.app.github.dev (alternate Codespaces format)
    if (hostname.includes('preview.app.github.dev')) {
      const backendHostname = hostname.replace(/-\d+\.preview\.app\.github\.dev$/, '-5000.preview.app.github.dev');
      return `https://${backendHostname}`;
    }
    
    // 4. Detect github.dev (Codespaces web editor)
    if (hostname.includes('github.dev')) {
      // This format is trickier - best to use environment variable
      console.warn('Running in github.dev - please set VITE_BACKEND_URL in .env file');
      return `https://${hostname.replace(/\.github\.dev.*/, '')}-5000.app.github.dev`;
    }
    
    // 5. Local development (localhost or 127.0.0.1)
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
      return `http://127.0.0.1:5000`;
    }
    
    // 6. Fallback - try to construct URL based on current location
    console.warn('Unable to auto-detect backend URL. Using fallback.');
    return `${protocol}//${hostname}:5000`;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { type: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);

    const backendUrl = getBackendUrl();
    console.log('Connecting to backend:', backendUrl);

    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.text }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      
      // Check if there's an error in the response
      if (data.error) {
        throw new Error(data.response || 'Unknown server error');
      }

      const botMessage = { type: 'bot', text: data.response };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error fetching bot response:', error);
      const errorMessage = { 
        type: 'bot', 
        text: `Error: ${error.message || 'Could not connect to the server. Make sure the backend is running on port 5000.'}` 
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      sendMessage();
    }
  };

  const clearchat = () => { 
    setMessages([]); 
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <span className="header-title">Chefbot</span>
          <button className="clear-button" onClick={clearchat}>clear</button>
        </div>
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="message bot">
              <em>Thinking...</em>
            </div>
          )}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button onClick={sendMessage} disabled={isLoading}>
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;