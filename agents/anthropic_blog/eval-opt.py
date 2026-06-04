import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv(override=True)

http_client_llm = httpx.Client(verify=True, timeout=30.0)
client_llm = OpenAI(
    base_url=os.environ['URL'],
    http_client=http_client_llm,
    api_key=os.environ['KEY'],
)

def llm_agent(prompt: str) -> str:
    response = client_llm.chat.completions.create(
        model="llama-3-1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def code_optimizer(code: str) -> str:
    """Generate improved version of the code"""
    prompt = f"""You are a Python expert. Improve the following code while maintaining its functionality.
    Focus on:
    - Code readability
    - Best practices
    - Performance optimization
    - Error handling
    
    Here's the code to improve:
    ```python
    {code}
    ```
    
    Provide only the improved code without explanations."""
    
    return llm_agent(prompt)

def code_evaluator(code: str) -> tuple[bool, str]:
    """Evaluate code quality and return (passed, feedback)"""
    prompt = f"""You are a strict Python code reviewer. Evaluate the following code for quality:
    ```python
    {code}
    ```
    
    Evaluate based on:
    1. Code readability and style (PEP 8)
    2. Error handling
    3. Performance considerations
    4. Best practices
    5. Security concerns
    
    Respond in the following format:
    PASSED: [true/false]
    FEEDBACK: [detailed feedback]
    """
    
    evaluation = llm_agent(prompt)
    
    # Parse evaluation response
    passed = "PASSED: true" in evaluation.lower()
    feedback = evaluation.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in evaluation else evaluation
    
    return passed, feedback

def evaluator_optimizer_workflow(initial_code: str, max_iterations: int = 3) -> tuple[str, list[str]]:
    """
    Workflow that iteratively improves code until it passes evaluation or reaches max iterations.
    Returns: (final_code, feedback_history)
    """
    current_code = initial_code
    feedback_history = []
    iterations = 0
    
    print("\n=== STARTING CODE EVALUATION WORKFLOW ===")
    print(f"Initial code:\n{initial_code}\n")
    
    while iterations < max_iterations:
        iterations += 1
        print(f"\n=== ITERATION {iterations} ===")
        
        # Evaluate current code
        passed, feedback = code_evaluator(current_code)
        feedback_history.append(f"Iteration {iterations} feedback: {feedback}")
        print(f"Evaluation feedback:\n{feedback}")
        
        if passed:
            print("\n✅ Code passed evaluation!")
            break
            
        print("\n⚠️ Code needs improvement. Optimizing...")
        # Optimize code based on feedback
        current_code = code_optimizer(current_code)
        print(f"\nOptimized code:\n{current_code}")
        
    if not passed and iterations == max_iterations:
        feedback_history.append("Maximum iterations reached without passing evaluation")
        print("\n⚠️ Maximum iterations reached without passing evaluation")
    
    return current_code, feedback_history

# Example usage:
if __name__ == "__main__":
    test_code = """
def calculate_average(numbers):
    sum = 0
    for n in numbers:
        sum += n
    return sum/len(numbers)
    """
    
    final_code, feedback_history = evaluator_optimizer_workflow(test_code)
    
    print("\n=== FINAL RESULTS ===")
    print("Feedback history:")
    for feedback in feedback_history:
        print(f"- {feedback}")
    print("\nFinal code:")
    print(final_code)