import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Fade,
  LinearProgress
} from '@mui/material';
import {
  Mic,
  MicOff,
  VolumeUp
} from '@mui/icons-material';

const VoiceInput = ({ isListening, onVoiceCommand, onListeningChange }) => {
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const recognitionRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();

      const recognition = recognitionRef.current;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsSupported(true);
        setTranscript('Listening...');
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          const transcript = result[0].transcript;

          if (result.isFinal) {
            finalTranscript += transcript;
            setConfidence(result[0].confidence);
          } else {
            interimTranscript += transcript;
          }
        }

        const fullTranscript = finalTranscript || interimTranscript;
        setTranscript(fullTranscript);

        // Process final transcript as voice command
        if (finalTranscript.trim() && onVoiceCommand) {
          onVoiceCommand(finalTranscript.trim());
          setTranscript(''); // Clear after processing
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setTranscript(`Error: ${event.error}`);
        onListeningChange(false);
      };

      recognition.onend = () => {
        if (isListening) {
          // Restart if we should still be listening
          setTimeout(() => {
            try {
              recognition.start();
            } catch (e) {
              console.error('Failed to restart recognition:', e);
              onListeningChange(false);
            }
          }, 100);
        }
      };

      setIsSupported(true);
    } else {
      setIsSupported(false);
      setTranscript('Speech recognition not supported in this browser');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // Handle listening state changes
  useEffect(() => {
    const recognition = recognitionRef.current;
    if (!recognition) return;

    if (isListening && isSupported) {
      try {
        recognition.start();
      } catch (e) {
        console.error('Failed to start recognition:', e);
        onListeningChange(false);
      }
    } else {
      recognition.stop();
      setTranscript('');
    }
  }, [isListening, isSupported, onListeningChange]);

  const commonCommands = [
    'Create a Python function',
    'Write a JavaScript loop',
    'Generate HTML structure',
    'Create a React component',
    'Write a sorting algorithm',
    'Make a REST API call'
  ];

  if (!isSupported) {
    return (
      <Paper 
        elevation={2} 
        sx={{ 
          position: 'fixed', 
          bottom: 80, 
          left: 16, 
          p: 2, 
          maxWidth: 300,
          bgcolor: 'error.light',
          color: 'error.contrastText'
        }}
      >
        <Typography variant="body2">
          Speech recognition is not supported in this browser. 
          Please use Chrome, Edge, or Safari for voice features.
        </Typography>
      </Paper>
    );
  }

  return (
    <Fade in={isListening || transcript.length > 0}>
      <Paper 
        elevation={4} 
        sx={{ 
          position: 'fixed', 
          bottom: 80, 
          left: 16, 
          p: 2, 
          maxWidth: 350,
          minWidth: 280,
          bgcolor: isListening ? 'primary.light' : 'background.paper',
          color: isListening ? 'primary.contrastText' : 'text.primary',
          border: isListening ? '2px solid' : '1px solid',
          borderColor: isListening ? 'primary.main' : 'divider'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <IconButton size="small" sx={{ mr: 1 }}>
            {isListening ? <Mic /> : <MicOff />}
          </IconButton>

          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Voice Input
          </Typography>
        </Box>

        {isListening && <LinearProgress sx={{ mb: 2 }} />}

        {transcript && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              {isListening ? 'Listening...' : 'Last Command:'}
            </Typography>
            <Typography variant="body2" sx={{ fontStyle: 'italic', p: 1, borderRadius: 1 }}>
              {transcript}
            </Typography>
          </Box>
        )}

        {!isListening && (
          <Box>
            <Typography variant="caption" sx={{ mb: 1, display: 'block' }}>
              Try saying:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {commonCommands.slice(0, 3).map((command, index) => (
                <Chip
                  key={index}
                  label={command}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>
    </Fade>
  );
};

export default VoiceInput;
