const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// Fixed Advanced dynamic language detection that works with ANY code
const detectLanguage = async (req, res) => {
  try {
    const { code } = req.body;
    
    const detectLanguageFromCode = (code) => {
      const trimmedCode = code.trim();
      
      if (!trimmedCode || trimmedCode.length === 0) return 'text';
      
      // Language patterns with comprehensive scoring system - FIXED with all required properties
      const languagePatterns = {
        'python': {
          keywords: ['def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'lambda', 'yield', 'return', 'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False'],
          functions: ['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'open', 'input', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'sum', 'min', 'max', 'abs', 'round'],
          patterns: [
            /^\s*def\s+\w+\s*\(/m,           // function definition
            /^\s*class\s+\w+.*:/m,           // class definition  
            /^\s*import\s+\w+/m,            // import statement
            /^\s*from\s+\w+\s+import/m,     // from import
            /^\s*if\s+__name__\s*==\s*['"]__main__['"]/m, // main check
            /^\s*#.*$/m,                    // comments
            /^\s*(if|elif|else|for|while|try|except|finally|with)\s*.*:/m, // control structures
            /^\s*@\w+/m,                    // decorators
            /\bprint\s*\(/,                 // print function
            /\brange\s*\(/,                 // range function
            /\blen\s*\(/,                   // len function
            /:\s*$/m,                       // lines ending with colon
            /^\s*\w+\s*=\s*\[.*\]/m,        // list assignment
            /^\s*\w+\s*=\s*{.*}/m,          // dict assignment
            /^\s*\w+\s*=\s*\(.*\)/m,        // tuple assignment
            /^\s*for\s+\w+\s+in\s+/m,       // for in loop
            /^\s*while\s+.*:/m,             // while loop
            /^\s*if\s+.*:/m,                // if statement
            /^\s*elif\s+.*:/m,              // elif statement
            /^\s*else\s*:/m,                // else statement
            /^\s*try\s*:/m,                 // try statement
            /^\s*except.*:/m,               // except statement
            /^\s*finally\s*:/m,             // finally statement
            /^\s*with\s+.*:/m,              // with statement
            /\bself\b/,                     // self keyword
            /\b__\w+__\b/,                  // magic methods
            /^\s*\w+\(.*\)\s*$/m,           // function calls
            /\bTrue\b|\bFalse\b|\bNone\b/,  // Python constants
            /\band\b|\bor\b|\bnot\b/,       // Python operators
            /\bin\b|\bis\b/,                // Python operators
            /^\s*\w+\s*\+=\s*\d+/m,         // += operator
            /f['"].*{.*}.*['"]/,            // f-strings
            /r['"].*['"]/,                  // raw strings
            /['"][^'"]*['"]\s*\.format/,    // string format
            /\w+\.\w+\(/,                   // method calls
            /\[\s*\d+\s*:\s*\d*\s*\]/,      // list slicing
            /^\s*\w+\s*=\s*\d+/m,           // simple assignment
            /^\s*\w+\s*=\s*['"]/m,          // string assignment
          ],
          negative: [
            /;$/m,                          // semicolons at end of line
            /\{[^}]*\}/,                    // curly braces for blocks
            /#include/,                     // C/C++ includes
            /\bvar\b|\blet\b|\bconst\b/,    // JS variable declarations
            /\bpublic\b|\bprivate\b|\bstatic\b/, // Java/C++ access modifiers
            /console\./,                    // JavaScript console
            /System\.out/,                  // Java System.out
          ]
        },
        
        'javascript': {
          keywords: ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'typeof', 'instanceof', 'new', 'this', 'super', 'class', 'extends', 'import', 'export', 'default', 'async', 'await'],
          functions: ['console', 'alert', 'prompt', 'confirm', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval', 'parseInt', 'parseFloat', 'isNaN', 'JSON', 'Math', 'Date', 'Array', 'Object', 'String', 'Number', 'Boolean', 'document', 'window'],
          patterns: [
            /^\s*function\s+\w+\s*\(/m,     // function declaration
            /^\s*(var|let|const)\s+\w+/m,  // variable declaration
            /^\s*console\.(log|error|warn|info)/m, // console methods
            /=>\s*{?/m,                    // arrow functions
            /^\s*if\s*\(/m,                // if statement
            /^\s*for\s*\(/m,               // for loop
            /^\s*while\s*\(/m,             // while loop
            /^\s*switch\s*\(/m,            // switch statement
            /^\s*try\s*{/m,                // try block
            /^\s*catch\s*\(/m,             // catch block
            /^\s*\/\/.*$/m,                // single line comments
            /\/\*[\s\S]*?\*\//,            // multi-line comments
            /^\s*class\s+\w+/m,            // class declaration
            /^\s*(import|export)\s+/m,     // ES6 imports/exports
            /^\s*async\s+function/m,       // async functions
            /^\s*await\s+/m,               // await keyword
            /\$\{.*\}/,                    // template literals
            /\bthis\./,                    // this keyword
            /\bnew\s+\w+\(/,               // constructor calls
            /\btypeof\s+/,                 // typeof operator
            /\binstanceof\s+/,             // instanceof operator
            /===|!==|==|!=/,               // JS equality operators
            /\|\||&&/,                     // logical operators
            /^\s*\w+\s*:\s*function/m,     // object method definition
            /^\s*\w+\s*:\s*\w+/m,          // object property
            /\[(\d+|\w+)\]/,               // array/object access
            /\.\w+\(/,                     // method calls
            /document\./,                  // DOM access
            /window\./,                    // window object
            /addEventListener|removeEventListener/, // event listeners
            /getElementById|querySelector/, // DOM queries
          ],
          negative: [
            /^\s*def\s+/m,                 // Python function def
            /:\s*$/m,                      // Python colons (unless in ternary)
            /^\s*#/m,                      // Python comments
            /^\s*import\s+\w+$/m,          // Python simple imports
            /System\./,                    // Java System
            /#include/,                    // C includes
          ]
        },
        
        'java': {
          keywords: ['public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized', 'volatile', 'transient', 'native', 'strictfp', 'class', 'interface', 'enum', 'extends', 'implements', 'import', 'package', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'throws', 'new', 'this', 'super', 'null', 'true', 'false'],
          functions: ['System', 'String', 'Integer', 'Double', 'Float', 'Long', 'Boolean', 'Character', 'Math', 'Arrays', 'Collections', 'List', 'ArrayList', 'HashMap', 'HashSet', 'Scanner', 'BufferedReader', 'FileReader'],
          patterns: [
            /^\s*public\s+class\s+\w+/m,   // public class
            /^\s*public\s+static\s+void\s+main/m, // main method
            /System\.(out|err)\.(print|println)/m, // System.out
            /^\s*package\s+[\w.]+;/m,      // package declaration
            /^\s*import\s+[\w.*]+;/m,      // import statement
            /^\s*(public|private|protected)\s+(static\s+)?(final\s+)?\w+\s+\w+\s*\(/m, // method declaration
            /^\s*(public|private|protected)\s+(static\s+)?(final\s+)?\w+\s+\w+\s*(=|;)/m, // field declaration
            /\bnew\s+\w+\s*\(/m,           // constructor calls
            /^\s*if\s*\(/m,                // if statement
            /^\s*for\s*\(/m,               // for loop
            /^\s*while\s*\(/m,             // while loop
            /^\s*try\s*\{/m,               // try block
            /^\s*catch\s*\(/m,             // catch block
            /^\s*\/\/.*$/m,                // single line comments
            /\/\*[\s\S]*?\*\//,            // multi-line comments
            /^\s*@\w+/m,                   // annotations
            /\bthis\./,                    // this reference
            /\bsuper\./,                   // super reference
            /\w+\s*\[\s*\]/,               // array declarations
            /\w+\<\w+\>/,                  // generics
            /instanceof\s+\w+/,            // instanceof operator
            /\bthrows\s+\w+/m,             // throws clause
            /^\s*}\s*catch/m,              // } catch pattern
            /^\s*}\s*finally/m,            // } finally pattern
            /Scanner\s+\w+/,               // Scanner usage
            /String\[\]/,                  // String array
            /Integer\.(parseInt|valueOf)/, // Integer methods
          ],
          negative: [
            /^\s*def\s+/m,                 // Python functions
            /^\s*function\s+/m,            // JavaScript functions
            /console\./,                   // JavaScript console
            /\bprint\s*\(/,                // Python print
            /#include/,                    // C includes
            /^\s*#/m,                      // Python comments
          ]
        },
        
        'cpp': {
          keywords: ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while', 'class', 'private', 'protected', 'public', 'friend', 'inline', 'operator', 'overload', 'template', 'this', 'virtual', 'bool', 'true', 'false', 'new', 'delete', 'namespace', 'using', 'try', 'catch', 'throw'],
          functions: ['cout', 'cin', 'endl', 'printf', 'scanf', 'malloc', 'free', 'strlen', 'strcpy', 'strcmp', 'vector', 'string', 'map', 'set', 'list', 'deque', 'stack', 'queue'],
          patterns: [
            /#include\s*<[\w.]+>/m,        // include headers
            /^\s*using\s+namespace\s+\w+;/m, // using namespace
            /^\s*int\s+main\s*\(/m,        // main function
            /std::/m,                      // std namespace
            /(cout|cin)\s*[<>]{1,2}/m,     // iostream operators
            /^\s*(public|private|protected)\s*:/m, // access specifiers
            /^\s*class\s+\w+/m,            // class declaration
            /^\s*struct\s+\w+/m,           // struct declaration
            /^\s*template\s*<.*>/m,        // template declaration
            /^\s*(virtual\s+)?\w+\s*\*?\s*\w+\s*\(/m, // function declaration
            /\w+::\w+/m,                   // scope resolution
            /->\w+/m,                      // pointer member access
            /^\s*#define\s+\w+/m,          // macro definition
            /^\s*#ifndef\s+\w+/m,          // header guards
            /^\s*#ifdef\s+\w+/m,           // conditional compilation
            /^\s*#endif/m,                 // end conditional
            /\bnew\s+\w+/m,                // new operator
            /\bdelete\s+\w+/m,             // delete operator
            /\bsizeof\s*\(/m,              // sizeof operator
            /^\s*\/\/.*$/m,                // single line comments
            /\/\*[\s\S]*?\*\//,            // multi-line comments
            /\*\w+/m,                      // pointers
            /&\w+/m,                       // references
            /^\s*\w+\s*\*+\s*\w+/m,        // pointer declarations
            /^\s*\w+\s*&\s*\w+/m,          // reference declarations
            /vector\s*<\w+>/,              // vector declarations
            /string\s+\w+/,                // string declarations
          ],
          negative: [
            /^\s*def\s+/m,                 // Python functions
            /^\s*function\s+/m,            // JavaScript functions
            /console\./,                   // JavaScript console
            /\bprint\s*\(/,                // Python print
            /System\./,                    // Java System
            /^\s*import\s+\w+$/m,          // Simple imports (not C++)
          ]
        },
        
        'c': {
          keywords: ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'],
          functions: ['printf', 'scanf', 'malloc', 'free', 'strlen', 'strcpy', 'strcmp', 'strcat', 'fopen', 'fclose', 'fprintf', 'fscanf', 'getchar', 'putchar', 'puts', 'gets'],
          patterns: [
            /#include\s*<[\w.]+\.h>/m,     // C header includes
            /^\s*int\s+main\s*\(/m,        // main function
            /printf\s*\(/m,                // printf function
            /scanf\s*\(/m,                 // scanf function
            /malloc\s*\(/m,                // malloc function
            /free\s*\(/m,                  // free function
            /^\s*struct\s+\w+/m,           // struct declaration
            /^\s*typedef\s+/m,             // typedef
            /^\s*#define\s+\w+/m,          // macro definition
            /^\s*#ifndef\s+\w+/m,          // header guards
            /^\s*#ifdef\s+\w+/m,           // conditional compilation
            /^\s*#endif/m,                 // end conditional
            /\*\w+/m,                      // pointers
            /&\w+/m,                       // address of
            /^\s*\w+\s*\*+\s*\w+/m,        // pointer declarations
            /->\w+/m,                      // struct member access
            /^\s*\/\*[\s\S]*?\*\//m,       // C style comments
            /sizeof\s*\(/m,                // sizeof operator
            /\w+\[\d*\]/m,                 // array declarations
            /"%[dscf%]"/m,                 // printf format strings
            /FILE\s*\*/,                   // file pointers
            /NULL/,                        // NULL constant
          ],
          negative: [
            /std::/m,                      // C++ namespace
            /cout|cin/m,                   // C++ iostream
            /class\s+/m,                   // C++ class
            /^\s*def\s+/m,                 // Python functions
            /console\./,                   // JavaScript console
            /System\./,                    // Java System
            /using\s+namespace/,           // C++ using
          ]
        },
        
        'html': {
          keywords: ['html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'select', 'option', 'textarea'],
          functions: [],
          patterns: [
            /<!DOCTYPE\s+html>/i,          // DOCTYPE declaration
            /<html[^>]*>/i,                // html tag
            /<head[^>]*>/i,                // head tag
            /<body[^>]*>/i,                // body tag
            /<title[^>]*>/i,               // title tag
            /<meta[^>]*>/i,                // meta tag
            /<link[^>]*>/i,                // link tag
            /<script[^>]*>/i,              // script tag
            /<style[^>]*>/i,               // style tag
            /<div[^>]*>/i,                 // div tag
            /<span[^>]*>/i,                // span tag
            /<p[^>]*>/i,                   // p tag
            /<h[1-6][^>]*>/i,              // heading tags
            /<a[^>]*>/i,                   // anchor tag
            /<img[^>]*>/i,                 // img tag
            /<(ul|ol)[^>]*>/i,             // list tags
            /<li[^>]*>/i,                  // list item
            /<table[^>]*>/i,               // table tag
            /<(tr|td|th)[^>]*>/i,          // table row/cell tags
            /<form[^>]*>/i,                // form tag
            /<input[^>]*>/i,               // input tag
            /<button[^>]*>/i,              // button tag
            /<(select|option)[^>]*>/i,     // select tags
            /<textarea[^>]*>/i,            // textarea tag
            /class\s*=\s*["'][^"']*["']/i, // class attribute
            /id\s*=\s*["'][^"']*["']/i,    // id attribute
            /src\s*=\s*["'][^"']*["']/i,   // src attribute
            /href\s*=\s*["'][^"']*["']/i,  // href attribute
            /<!--[\s\S]*?-->/,             // HTML comments
            /<\w+[^>]*\/?>/,               // any HTML tag
            /<\/\w+>/,                     // closing tags
            /<\w+.*>/,                     // opening tags
          ],
          negative: [
            /function\s*\(/,               // JavaScript functions
            /console\./,                   // JavaScript console
            /\bprint\s*\(/,                // Python print
            /printf\s*\(/,                 // C printf
            /System\./,                    // Java System
          ]
        },
        
        'css': {
          keywords: ['color', 'background', 'font', 'margin', 'padding', 'border', 'width', 'height', 'display', 'position', 'top', 'left', 'right', 'bottom', 'float', 'clear', 'overflow', 'visibility', 'z-index'],
          functions: [],
          patterns: [
            /\.[a-zA-Z_-][a-zA-Z0-9_-]*\s*\{/,  // class selectors
            /#[a-zA-Z_-][a-zA-Z0-9_-]*\s*\{/,    // id selectors
            /\w+\s*\{[^}]*\}/,                    // element selectors
            /\w+\s*:\s*[^;]+;/,                   // property: value;
            /@media[^{]*\{/,                      // media queries
            /@import\s+/,                         // import statements
            /@keyframes\s+\w+/,                   // keyframe animations
            /\*\s*\{[^}]*\}/,                     // universal selector
            /\w+:\w+/,                            // pseudo-classes
            /\w+::\w+/,                           // pseudo-elements
            /\w+\[\w+.*\]/,                       // attribute selectors
            /\w+\s*>\s*\w+/,                      // child selectors
            /\w+\s*\+\s*\w+/,                     // adjacent sibling
            /\w+\s*~\s*\w+/,                      // general sibling
            /\/\*[\s\S]*?\*\//,                   // CSS comments
            /rgb\s*\(/,                           // rgb colors
            /rgba\s*\(/,                          // rgba colors
            /hsl\s*\(/,                           // hsl colors
            /#[0-9A-Fa-f]{3,6}/,                 // hex colors
            /\d+px|\d+em|\d+rem|\d+%/,           // CSS units
            /!important/,                         // important declaration
          ],
          negative: [
            /console\./,                          // JavaScript
            /\bprint\s*\(/,                       // Python
            /printf\s*\(/,                        // C
            /<\w+>/,                              // HTML tags
            /function\s*\(/,                      // Functions
          ]
        }
      };
      
      // Calculate scores for each language
      let scores = {};
      for (const lang in languagePatterns) {
        scores[lang] = 0;
      }
      
      // Score based on patterns, keywords, and functions
      for (const [lang, config] of Object.entries(languagePatterns)) {
        let score = 0;
        
        // Pattern matching (highest weight)
        for (const pattern of config.patterns) {
          const matches = (code.match(pattern) || []).length;
          score += matches * 3; // Pattern matches get 3 points each
        }
        
        // Keyword matching
        const lowerCode = code.toLowerCase();
        for (const keyword of config.keywords) {
          const regex = new RegExp('\\b' + keyword + '\\b', 'gi');
          const matches = (code.match(regex) || []).length;
          score += matches * 1; // Keyword matches get 1 point each
        }
        
        // Function matching - FIXED: Check if functions array exists and is not empty
        if (config.functions && Array.isArray(config.functions) && config.functions.length > 0) {
          for (const func of config.functions) {
            const regex = new RegExp('\\b' + func + '\\b', 'gi');
            const matches = (code.match(regex) || []).length;
            score += matches * 2; // Function matches get 2 points each
          }
        }
        
        // Negative patterns (reduce score significantly)
        if (config.negative && Array.isArray(config.negative)) {
          for (const pattern of config.negative) {
            const matches = (code.match(pattern) || []).length;
            score -= matches * 5; // Negative matches reduce score by 5
          }
        }
        
        scores[lang] = Math.max(0, score); // Ensure score doesn't go negative
      }
      
      // Find the language with the highest score
      let maxScore = 0;
      let detectedLanguage = 'text';
      
      for (const [lang, score] of Object.entries(scores)) {
        if (score > maxScore) {
          maxScore = score;
          detectedLanguage = lang;
        }
      }
      
      // Additional comprehensive fallback detection
      if (maxScore === 0 || maxScore < 3) {
        const codeLines = code.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        
        // Check for specific language indicators
        for (const line of codeLines) {
          // Python indicators
          if (/^\s*(def|class|import|from|if|for|while|try|with)\s+/.test(line) ||
              /:\s*$/.test(line) ||
              /^\s*#/.test(line) ||
              /\bprint\s*\(/.test(line) ||
              /\b(len|range|str|int|float|list|dict|set|tuple)\s*\(/.test(line)) {
            return 'python';
          }
          
          // JavaScript indicators
          if (/^\s*(function|var|let|const|if|for|while|switch)\s+/.test(line) ||
              /console\.(log|error|warn|info)/.test(line) ||
              /=>\s*\{?/.test(line) ||
              /document\./.test(line) ||
              /window\./.test(line)) {
            return 'javascript';
          }
          
          // Java indicators
          if (/^\s*(public|private|protected)\s+/.test(line) ||
              /System\.(out|err)\./.test(line) ||
              /^\s*package\s+/.test(line) ||
              /^\s*import\s+[\w.]+;/.test(line)) {
            return 'java';
          }
          
          // C++ indicators
          if (/#include\s*<\w+>/.test(line) ||
              /std::/.test(line) ||
              /using\s+namespace/.test(line) ||
              /(cout|cin)\s*[<>]/.test(line)) {
            return 'cpp';
          }
          
          // C indicators
          if (/#include\s*<\w+\.h>/.test(line) ||
              /(printf|scanf|malloc|free)\s*\(/.test(line)) {
            return 'c';
          }
          
          // HTML indicators
          if (/<\w+[^>]*>/i.test(line) ||
              /<!DOCTYPE/i.test(line)) {
            return 'html';
          }
          
          // CSS indicators
          if (/\w+\s*\{[^}]*\}/.test(line) ||
              /\w+\s*:\s*[^;]+;/.test(line) ||
              /\.[a-zA-Z_-][\w-]*\s*\{/.test(line) ||
              /#[a-zA-Z_-][\w-]*\s*\{/.test(line)) {
            return 'css';
          }
        }
      }
      
      return detectedLanguage;
    };
    
    const detectedLanguage = detectLanguageFromCode(code);
    const confidence = detectedLanguage !== 'text' ? 0.85 : 0.1;
    
    console.log(`Code: ${code.substring(0, 100)}...`);
    console.log(`Detected language: ${detectedLanguage} with confidence: ${confidence}`);
    
    res.json({ language: detectedLanguage, confidence });
  } catch (error) {
    console.error('Language detection error:', error);
    res.status(500).json({ error: 'Language detection failed' });
  }
};

// Enhanced code execution with better error handling
const executeCode = async (req, res) => {
  try {
    const { code, language, input = '' } = req.body;
    const fileId = uuidv4();
    const tempDir = path.join(__dirname, '../temp');
    
    // Create temp directory if it doesn't exist
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    const executeCodeByLanguage = async (code, language, fileId, input) => {
      const tempPath = path.join(tempDir, fileId);
      
      switch (language.toLowerCase()) {
        case 'python':
          const pyFile = `${tempPath}.py`;
          fs.writeFileSync(pyFile, code);
          return new Promise((resolve) => {
            exec(`python "${pyFile}"`, { input, timeout: 10000 }, (error, stdout, stderr) => {
              try { fs.unlinkSync(pyFile); } catch (e) {}
              resolve({
                success: !error,
                output: stdout || stderr || 'No output',
                error: error ? error.message : null
              });
            });
          });
          
        case 'javascript':
          const jsFile = `${tempPath}.js`;
          fs.writeFileSync(jsFile, code);
          return new Promise((resolve) => {
            exec(`node "${jsFile}"`, { input, timeout: 10000 }, (error, stdout, stderr) => {
              try { fs.unlinkSync(jsFile); } catch (e) {}
              resolve({
                success: !error,
                output: stdout || stderr || 'No output',
                error: error ? error.message : null
              });
            });
          });
          
        case 'java':
          const javaFile = `${tempPath}.java`;
          let className = 'Main';
          
          // Extract class name from code if it exists
          const classMatch = code.match(/public\s+class\s+(\w+)/);
          if (classMatch) {
            className = classMatch[1];
          }
          
          // Wrap simple statements in a main method if needed
          let javaCode = code;
          if (!code.includes('public static void main') && !code.includes('public class')) {
            javaCode = `public class ${className} {
  public static void main(String[] args) {
    ${code}
  }
}`;
          }
          
          fs.writeFileSync(javaFile, javaCode);
          return new Promise((resolve) => {
            exec(`javac "${javaFile}" && java -cp "${path.dirname(javaFile)}" ${className}`, 
                 { input, timeout: 15000 }, (error, stdout, stderr) => {
              try {
                fs.unlinkSync(javaFile);
                fs.unlinkSync(`${path.dirname(javaFile)}/${className}.class`);
              } catch (e) {}
              resolve({
                success: !error,
                output: stdout || stderr || 'No output',
                error: error ? error.message : null
              });
            });
          });
          
        case 'cpp':
        case 'c++':
          const cppFile = `${tempPath}.cpp`;
          const exeFile = process.platform === 'win32' ? `${tempPath}.exe` : `${tempPath}`;
          
          // Add basic includes if not present
          let cppCode = code;
          if (!code.includes('#include')) {
            cppCode = `#include <iostream>
#include <string>
using namespace std;

${code}`;
          }
          
          fs.writeFileSync(cppFile, cppCode);
          return new Promise((resolve) => {
            const compileCmd = process.platform === 'win32' 
              ? `g++ "${cppFile}" -o "${exeFile}" && "${exeFile}"`
              : `g++ "${cppFile}" -o "${exeFile}" && "${exeFile}"`;
            exec(compileCmd, { input, timeout: 15000 }, (error, stdout, stderr) => {
              try {
                fs.unlinkSync(cppFile);
                if (fs.existsSync(exeFile)) fs.unlinkSync(exeFile);
              } catch (e) {}
              resolve({
                success: !error,
                output: stdout || stderr || 'No output',
                error: error ? error.message : null
              });
            });
          });
          
        case 'c':
          const cFile = `${tempPath}.c`;
          const cExeFile = process.platform === 'win32' ? `${tempPath}.exe` : `${tempPath}`;
          
          // Add basic includes if not present
          let cCode = code;
          if (!code.includes('#include')) {
            cCode = `#include <stdio.h>
#include <stdlib.h>
#include <string.h>

${code}`;
          }
          
          fs.writeFileSync(cFile, cCode);
          return new Promise((resolve) => {
            const compileCmd = process.platform === 'win32'
              ? `gcc "${cFile}" -o "${cExeFile}" && "${cExeFile}"`
              : `gcc "${cFile}" -o "${cExeFile}" && "${cExeFile}"`;
            exec(compileCmd, { input, timeout: 15000 }, (error, stdout, stderr) => {
              try {
                fs.unlinkSync(cFile);
                if (fs.existsSync(cExeFile)) fs.unlinkSync(cExeFile);
              } catch (e) {}
              resolve({
                success: !error,
                output: stdout || stderr || 'No output',
                error: error ? error.message : null
              });
            });
          });
          
        default:
          return { success: false, error: `Language ${language} not supported yet` };
      }
    };
    
    const result = await executeCodeByLanguage(code, language, fileId, input);
    res.json(result);
    
  } catch (error) {
    console.error('Code execution error:', error);
    res.status(500).json({ error: 'Code execution failed' });
  }
};

module.exports = { detectLanguage, executeCode };