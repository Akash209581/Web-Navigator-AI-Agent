import React, { useRef, useEffect } from 'react';
import {
  Box,
  Toolbar,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Clear,
  FileCopy,
  Download
} from '@mui/icons-material';

const Terminal = ({ output, isRunning, onClear }) => {
  const terminalRef = useRef(null);

  // Auto-scroll to bottom when new output is added
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output]);

  const handleClear = () => {
    if (onClear) {
      onClear();
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(output);
    } catch (err) {
      console.error('Failed to copy output:', err);
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([output], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'output.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Terminal Toolbar */}
      <Toolbar variant="dense" sx={{ minHeight: 48, bgcolor: '#1e1e1e', color: 'white' }}>
        <Typography variant="subtitle2" sx={{ flexGrow: 1, color: 'white' }}>
          Output Terminal
        </Typography>

        {isRunning && (
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            <CircularProgress size={16} color="inherit" />
            <Typography variant="caption" sx={{ ml: 1, color: 'white' }}>
              Running...
            </Typography>
          </Box>
        )}

        <Tooltip title="Copy Output">
          <IconButton onClick={handleCopy} size="small" sx={{ color: 'white' }}>
            <FileCopy fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Download Output">
          <IconButton onClick={handleDownload} size="small" sx={{ color: 'white' }}>
            <Download fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Clear Terminal">
          <IconButton onClick={handleClear} size="small" sx={{ color: 'white' }}>
            <Clear fontSize="small" />
          </IconButton>
        </Tooltip>
      </Toolbar>

      {/* Terminal Content */}
      <Box
        ref={terminalRef}
        className="terminal"
        sx={{
          flexGrow: 1,
          height: 'calc(100% - 48px)',
          overflow: 'auto',
          fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          fontSize: '14px',
          lineHeight: 1.4,
          padding: 2,
          bgcolor: '#1e1e1e',
          color: '#d4d4d4',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}
      >
        {output || 'Ready to execute code...\nClick the play button or press Ctrl+R to run your code.'}
      </Box>
    </Box>
  );
};

export default Terminal;
