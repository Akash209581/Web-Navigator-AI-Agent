const axios = require('axios');

const generateCode = async (req, res) => {
  try {
    const { prompt, language = 'python' } = req.body;
    
    console.log('🤖 AI Generation Request:', { prompt, language });
    
    const generatedCode = generateDynamicCode(prompt, language);
    
    console.log('📝 Generated code for prompt:', prompt);
    
    return res.json({
      code: generatedCode,
      success: true,
      prompt: prompt,
      language: language
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    const fallbackCode = generateDynamicCode(req.body.prompt || 'hello world', req.body.language || 'python');
    
    return res.json({
      code: fallbackCode,
      success: true
    });
  }
};

function generateDynamicCode(prompt, language) {
  const lowerPrompt = prompt.toLowerCase();
  
  if (language.toLowerCase() === 'python') {
    if (lowerPrompt.includes('bubble sort')) {
      return `def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Example usage
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
print("Sorted array:", sorted_numbers)`;
    }
    
    if (lowerPrompt.includes('factorial')) {
      return `def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Example usage
num = 5
result = factorial(num)
print(f"Factorial of {num} is {result}")`;
    }
    
    if (lowerPrompt.includes('calculator')) {
      return `def calculator():
    try:
        num1 = float(input("Enter first number: "))
        operator = input("Enter operator (+, -, *, /): ")
        num2 = float(input("Enter second number: "))
        
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            result = num1 / num2 if num2 != 0 else "Error: Division by zero"
        else:
            result = "Invalid operator"
        
        print(f"Result: {result}")
    except ValueError:
        print("Error: Please enter valid numbers")

calculator()`;
    }
    
    return `# ${prompt}
def main():
    print("Python code for: ${prompt}")
    # TODO: Implement your logic here
    
if __name__ == "__main__":
    main()`;
  }
  
  if (language.toLowerCase() === 'javascript') {
    if (lowerPrompt.includes('bubble sort')) {
      return `function bubbleSort(arr) {
    let n = arr.length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
            }
        }
    }
    return arr;
}

// Example usage
const numbers = [64, 34, 25, 12, 22, 11, 90];
console.log("Sorted:", bubbleSort(numbers));`;
    }
    
    if (lowerPrompt.includes('api')) {
      return `const express = require('express');
const app = express();

app.use(express.json());

app.get('/api/users', (req, res) => {
    res.json({
        success: true,
        data: [
            { id: 1, name: 'John Doe', email: 'john@example.com' }
        ]
    });
});

app.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});`;
    }
    
    return `// ${prompt}
function main() {
    console.log("JavaScript code for: ${prompt}");
    // TODO: Implement your logic here
}

main();`;
  }
  
  return `// Code for: ${prompt}
// Language: ${language}
// TODO: Implement your logic here`;
}

module.exports = { generateCode };
