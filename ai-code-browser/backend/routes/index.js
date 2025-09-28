const express = require('express');
const router = express.Router();
const codeController = require('../controllers/codeController');
const aiController = require('../controllers/aiController');

router.post('/detect-language', codeController.detectLanguage);
router.post('/execute', codeController.executeCode);
router.post('/generate-code', aiController.generateCode);

router.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    ai_provider: 'dynamic_code_generation',
    node_env: process.env.NODE_ENV || 'development'
  });
});

router.post('/test-ai', async (req, res) => {
  try {
    const testPrompt = req.body.prompt || 'create a hello world function';
    const testLanguage = req.body.language || 'python';
    
    const mockReq = {
      body: {
        prompt: testPrompt,
        language: testLanguage
      }
    };
    
    const mockRes = {
      json: (data) => res.json(data)
    };
    
    await aiController.generateCode(mockReq, mockRes);
    
  } catch (error) {
    res.status(500).json({
      error: 'Test AI generation failed',
      message: error.message
    });
  }
});

router.get('/docs', (req, res) => {
  res.json({
    title: 'AI Code Browser API',
    version: '1.0.0',
    endpoints: {
      'GET /api/health': 'Health check',
      'POST /api/generate-code': 'Generate code dynamically',
      'POST /api/detect-language': 'Detect code language',
      'POST /api/execute': 'Execute code',
      'POST /api/test-ai': 'Test AI generation'
    }
  });
});

module.exports = router;
