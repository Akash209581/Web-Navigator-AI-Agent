#!/bin/bash

echo "🚀 Setting up AI Code Browser..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Node.js $(node --version) found"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ npm $(npm --version) found"

# Setup backend
echo "📦 Setting up backend..."
cd backend || exit
npm install
if [ ! -f ".env" ]; then
    cp ../.env.example .env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
fi
cd ..

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend || exit
npm install
cd ..

# Create start scripts
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
npm run dev
EOF
chmod +x start-backend.sh

cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run electron-dev
EOF
chmod +x start-frontend.sh

cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting AI Code Browser..."
cd backend && npm run dev &
BACKEND_PID=$!
sleep 5
cd ../frontend && npm run electron-dev
kill $BACKEND_PID 2>/dev/null
EOF
chmod +x start-all.sh

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Run: ./start-all.sh"
echo "3. The app will open as an Electron desktop application"
