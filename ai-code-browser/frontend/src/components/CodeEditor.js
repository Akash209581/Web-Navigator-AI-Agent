import React, { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import {
  Box,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Toolbar,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Settings,
  Fullscreen,
  FullscreenExit,
  Brightness4,
  Brightness7
} from '@mui/icons-material';

const CodeEditor = ({ code, language, onChange, onLanguageChange }) => {
  const [theme, setTheme] = useState('vs-dark');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const editorRef = useRef(null);

  const supportedLanguages = [
    { value: 'javascript', label: 'JavaScript' },
    { value: 'python', label: 'Python' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
    { value: 'html', label: 'HTML' },
    { value: 'css', label: 'CSS' },
    { value: 'json', label: 'JSON' },
    { value: 'xml', label: 'XML' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'php', label: 'PHP' },
    { value: 'ruby', label: 'Ruby' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'sql', label: 'SQL' }
  ];

  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
    fontSize: fontSize,
    fontFamily: 'Consolas, Monaco, "Courier New", monospace',
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    lineNumbers: 'on',
    renderLineHighlight: 'all',
    contextmenu: true,
    mouseWheelZoom: true,
    formatOnPaste: true,
    formatOnType: true,
    autoIndent: 'advanced',
    tabSize: 2,
    insertSpaces: true,
    dragAndDrop: true
  };

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;

    // Add custom key bindings
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Save functionality
      console.log('Save triggered');
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyR, () => {
      // Run code functionality
      window.dispatchEvent(new CustomEvent('runCode'));
    });
  };

  const toggleTheme = () => {
    const newTheme = theme === 'vs-dark' ? 'light' : 'vs-dark';
    setTheme(newTheme);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const formatCode = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Editor Toolbar */}
      <Toolbar variant="dense" sx={{ minHeight: 48, bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
          Code Editor
        </Typography>

        <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
          <InputLabel>Language</InputLabel>
          <Select
            value={language}
            label="Language"
            onChange={(e) => onLanguageChange(e.target.value)}
          >
            {supportedLanguages.map((lang) => (
              <MenuItem key={lang.value} value={lang.value}>
                {lang.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Tooltip title="Toggle Theme">
          <IconButton onClick={toggleTheme} size="small">
            {theme === 'vs-dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Tooltip>

        <Tooltip title="Format Code">
          <IconButton onClick={formatCode} size="small">
            <Settings />
          </IconButton>
        </Tooltip>

        <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
          <IconButton onClick={toggleFullscreen} size="small">
            {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
          </IconButton>
        </Tooltip>
      </Toolbar>

      {/* Monaco Editor */}
      <Box sx={{ flexGrow: 1, height: 'calc(100% - 48px)' }}>
        <Editor
          height="100%"
          language={language}
          value={code}
          theme={theme}
          options={editorOptions}
          onChange={onChange}
          onMount={handleEditorDidMount}
          loading={
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Typography>Loading editor...</Typography>
            </Box>
          }
        />
      </Box>
    </Box>
  );
};

export default CodeEditor;
