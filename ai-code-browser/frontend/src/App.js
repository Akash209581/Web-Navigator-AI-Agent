import React, { useState, useEffect, useCallback } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Fab,
  Snackbar,
  Alert
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Mic,
  MicOff,
  SmartToy,
  Code,
  Language
} from '@mui/icons-material';

import CodeEditor from './components/CodeEditor';
import Terminal from './components/Terminal';
import VoiceInput from './components/VoiceInput';
import AIAssistant from './components/AIAssistant';
import './App.css';

function App() {
  const [code, setCode] = useState('// Welcome to AI Code Browser\n// Type your code here or use voice commands\n\nconsole.log("Hello, World!");');
  const [language, setLanguage] = useState('javascript');
  const [output, setOutput] = useState('Ready to execute code...\n');
  const [isRunning, setIsRunning] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showAI, setShowAI] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  // Handle Electron menu actions
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.onMenuAction((event, action) => {
        switch (action) {
          case 'menu-run-code':
            handleRunCode();
            break;
          case 'menu-generate-code':
            setShowAI(true);
            break;
          case 'menu-start-voice':
            setIsListening(true);
            break;
          case 'menu-stop-voice':
            setIsListening(false);
            break;
          default:
            break;
        }
      });
    }
  }, []);

  // Auto-detect language when code changes
  const detectLanguage = useCallback(async (code) => {
    try {
      const response = await fetch('http://localhost:5000/api/detect-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.language !== language) {
          setLanguage(result.language);
          showNotification(`Language detected: ${result.language}`, 'success');
        }
      }
    } catch (error) {
      console.error('Language detection failed:', error);
    }
  }, [language]);

  // Debounced language detection
  useEffect(() => {
    const timer = setTimeout(() => {
      if (code.trim().length > 20) {
        detectLanguage(code);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [code, detectLanguage]);

  // Execute code
  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput('Executing code...\n');

    try {
      const response = await fetch('http://localhost:5000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language })
      });

      const result = await response.json();

      if (result.success) {
        setOutput(result.output || 'Code executed successfully!');
        showNotification('Code executed successfully!', 'success');
      } else {
        setOutput(result.error || 'Execution failed');
        showNotification('Execution failed', 'error');
      }
    } catch (error) {
      setOutput(`Error: ${error.message}`);
      showNotification('Network error', 'error');
    } finally {
      setIsRunning(false);
    }
  };

  // Handle voice command
  const handleVoiceCommand = async (command) => {
    showNotification(`Voice command: ${command}`, 'info');

    try {
      const response = await fetch('http://localhost:5000/api/generate-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: command, language })
      });

      if (response.ok) {
        const result = await response.json();
        setCode(result.code);
        showNotification('Code generated successfully!', 'success');
      }
    } catch (error) {
      showNotification('Failed to generate code', 'error');
    }
  };

  // Show notification
  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  return (
    <div className="App">
      <AppBar position="static" color="primary">
        <Toolbar>
          <Code sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Code Browser
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Language />
            <Typography variant="body2">
              {language.toUpperCase()}
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2, mb: 2 }}>
        <Grid container spacing={2}>
          {/* Code Editor */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ height: 'calc(100vh - 200px)' }}>
              <CodeEditor
                code={code}
                language={language}
                onChange={setCode}
                onLanguageChange={setLanguage}
              />
            </Paper>
          </Grid>

          {/* Terminal/Output */}
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ height: 'calc(100vh - 200px)' }}>
              <Terminal
                output={output}
                isRunning={isRunning}
              />
            </Paper>
          </Grid>
        </Grid>

        {/* Floating Action Buttons */}
        <Box sx={{ position: 'fixed', bottom: 16, right: 16, display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Fab
            color="primary"
            onClick={handleRunCode}
            disabled={isRunning}
          >
            {isRunning ? <Stop /> : <PlayArrow />}
          </Fab>

          <Fab
            color={isListening ? "secondary" : "default"}
            onClick={() => setIsListening(!isListening)}
          >
            {isListening ? <MicOff /> : <Mic />}
          </Fab>

          <Fab
            color="info"
            onClick={() => setShowAI(true)}
          >
            <SmartToy />
          </Fab>
        </Box>

        {/* Voice Input Component */}
        <VoiceInput
          isListening={isListening}
          onVoiceCommand={handleVoiceCommand}
          onListeningChange={setIsListening}
        />

        {/* AI Assistant Dialog */}
        <AIAssistant
          open={showAI}
          onClose={() => setShowAI(false)}
          onCodeGenerated={setCode}
          currentLanguage={language}
        />

        {/* Notification Snackbar */}
        <Snackbar
          open={notification.open}
          autoHideDuration={4000}
          onClose={() => setNotification({ ...notification, open: false })}
        >
          <Alert severity={notification.severity} sx={{ width: '100%' }}>
            {notification.message}
          </Alert>
        </Snackbar>
      </Container>
    </div>
  );
}

export default App;
