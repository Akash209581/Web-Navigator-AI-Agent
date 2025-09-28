import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Button,
  Box,
  Typography,
  Paper,
  IconButton,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Send,
  Close,
  ContentCopy,
  AutoFixHigh,
  Code,
  SmartToy
} from '@mui/icons-material';

const AIAssistant = ({ open, onClose, onCodeGenerated, currentLanguage }) => {
  const [prompt, setPrompt] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(currentLanguage);
  const messagesEndRef = useRef(null);

  const supportedLanguages = [
    'javascript', 'python', 'java', 'cpp', 'c', 'html', 'css', 
    'typescript', 'php', 'ruby', 'go', 'rust', 'sql'
  ];

  const quickPrompts = [
    'Create a function to sort an array',
    'Generate a REST API endpoint',
    'Write a unit test',
    'Create a simple web page',
    'Generate a database schema',
    'Write a recursive algorithm'
  ];

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation]);

  useEffect(() => {
    setSelectedLanguage(currentLanguage);
  }, [currentLanguage]);

  const handleSubmit = async (customPrompt = null) => {
    const messagePrompt = customPrompt || prompt;
    if (!messagePrompt.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messagePrompt,
      timestamp: new Date()
    };

    setConversation(prev => [...prev, userMessage]);
    setPrompt('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/generate-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt: messagePrompt, 
          language: selectedLanguage 
        })
      });

      if (response.ok) {
        const result = await response.json();

        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: result.code,
          language: selectedLanguage,
          timestamp: new Date()
        };

        setConversation(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Failed to generate code');
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I couldn\'t generate code at the moment. Please try again.',
        timestamp: new Date()
      };
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUseCode = (code) => {
    onCodeGenerated(code);
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '80vh', display: 'flex', flexDirection: 'column' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SmartToy color="primary" />
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          AI Code Assistant
        </Typography>
        <IconButton onClick={onClose} size="small">
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <FormControl size="small" sx={{ mb: 2, minWidth: 150 }}>
          <InputLabel>Target Language</InputLabel>
          <Select
            value={selectedLanguage}
            label="Target Language"
            onChange={(e) => setSelectedLanguage(e.target.value)}
          >
            {supportedLanguages.map((lang) => (
              <MenuItem key={lang} value={lang}>
                {lang.toUpperCase()}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {conversation.length === 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Quick Prompts:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {quickPrompts.map((quickPrompt, index) => (
                <Chip
                  key={index}
                  label={quickPrompt}
                  size="small"
                  clickable
                  onClick={() => handleSubmit(quickPrompt)}
                  icon={<AutoFixHigh />}
                />
              ))}
            </Box>
          </Box>
        )}

        <Box sx={{ flex: 1, overflow: 'auto', mb: 2 }}>
          {conversation.map((message) => (
            <Paper
              key={message.id}
              elevation={1}
              sx={{ p: 2, mb: 2 }}
            >
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {message.type === 'user' ? 'You' : 'AI Assistant'}
              </Typography>

              {message.type === 'ai' ? (
                <Box>
                  <Box sx={{ 
                    bgcolor: '#1e1e1e', 
                    color: '#d4d4d4', 
                    p: 2, 
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    mb: 2
                  }}>
                    <pre style={{ margin: 0 }}>{message.content}</pre>
                  </Box>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<Code />}
                    onClick={() => handleUseCode(message.content)}
                  >
                    Use This Code
                  </Button>
                </Box>
              ) : (
                <Typography variant="body2">
                  {message.content}
                </Typography>
              )}
            </Paper>
          ))}

          {isLoading && (
            <Paper elevation={1} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
              <CircularProgress size={20} sx={{ mr: 2 }} />
              <Typography variant="body2">AI is generating code...</Typography>
            </Paper>
          )}

          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder="Describe the code you want me to generate..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            disabled={isLoading}
          />
          <Button
            variant="contained"
            onClick={() => handleSubmit()}
            disabled={!prompt.trim() || isLoading}
            sx={{ minWidth: 60 }}
          >
            <Send />
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default AIAssistant;
