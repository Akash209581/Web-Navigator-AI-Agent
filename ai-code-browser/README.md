# AI-Powered Browser with Code Compilation

A revolutionary desktop application that combines web browsing capabilities with an intelligent code editor featuring AI-powered code generation, voice commands, and multi-language compilation support.

## 🚀 Features

### Core Functionality
- **Multi-language Code Editor** - Monaco Editor with syntax highlighting for 15+ languages
- **Intelligent Code Execution** - Compile and run code in Python, Java, C++, C, JavaScript, and more
- **AI Code Generation** - Generate code from natural language prompts using GPT-3.5
- **Voice Commands** - Control the application and generate code using voice input
- **Auto Language Detection** - Automatically detect programming language from code content
- **Browser Integration** - Built-in web browser functionality with Electron

### Advanced Features
- **Real-time Compilation** - Execute code with live output display
- **Voice-to-Text** - Convert speech to code generation commands
- **Smart Suggestions** - AI-powered code completion and suggestions
- **Multi-theme Support** - Light and dark themes for comfortable coding
- **Terminal Integration** - Built-in terminal for code execution output

## 🛠️ Technology Stack

### Frontend
- **Electron** - Cross-platform desktop application framework
- **React** - User interface library
- **Material-UI** - Modern UI components
- **Monaco Editor** - VS Code-powered code editor
- **Web Speech API** - Voice recognition and synthesis

### Backend
- **Node.js** - Server runtime
- **Express** - Web application framework
- **Child Process** - Code compilation and execution
- **OpenAI API** - AI code generation
- **Guesslang** - Programming language detection

## 📦 Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Python 3.x (for Python code execution)
- Java JDK (for Java code execution)
- GCC/G++ (for C/C++ code execution)
- OpenAI API key (for AI features)

### Quick Setup

#### Option 1: Automated Setup
```bash
# Linux/macOS
./setup.sh

# Windows
setup.bat
```

#### Option 2: Manual Setup
```bash
# 1. Install backend dependencies
cd backend
npm install
cp .env.example .env
# Edit .env and add your OpenAI API key

# 2. Install frontend dependencies
cd ../frontend
npm install

# 3. Start the application
cd ../backend && npm run dev &
cd ../frontend && npm run electron-dev
```

## 🎮 Usage

### Basic Operations
1. **Write Code**: Use the Monaco editor to write code in any supported language
2. **Run Code**: Click the play button or press Ctrl+R to execute code
3. **Voice Commands**: Click the microphone button and speak commands
4. **AI Assistant**: Click the AI button to open the chat interface

### Voice Commands Examples
- "Create a Python function to calculate factorial"
- "Generate a JavaScript function for API calls"
- "Write a Java class for student management"
- "Create HTML structure for a login page"

### Keyboard Shortcuts
- `Ctrl+R` - Run code
- `Ctrl+G` - Generate code with AI
- `Ctrl+Shift+V` - Start voice input

## 🔧 Supported Languages
- JavaScript/TypeScript
- Python
- Java
- C/C++
- HTML/CSS
- PHP, Ruby, Go, Rust, SQL

## 🔐 Security Features
- **Sandboxed Execution** - Code runs in isolated environment
- **Rate Limiting** - Prevents API abuse
- **Input Validation** - Sanitizes user input
- **CORS Protection** - Secure cross-origin requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🐛 Troubleshooting

### Common Issues

1. **Voice recognition not working**
   - Use Chrome, Edge, or Safari
   - Check microphone permissions

2. **Code compilation fails**
   - Verify compilers are installed
   - Check file permissions

3. **AI features not working**
   - Add OpenAI API key to .env file
   - Check network connectivity

For more issues, please check the documentation.
