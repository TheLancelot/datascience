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

def worker_1(task: str) -> str:
    """First worker that handles a specific subtask"""
    prompt = f"""You are Worker 1, specialized in breaking down and analyzing tasks.
    Please analyze the following task and provide detailed insights:
    {task}"""
    return llm_agent(prompt)

def worker_2(task: str) -> str:
    """Second worker that handles a specific subtask"""
    prompt = f"""You are Worker 2, specialized in synthesizing information and providing solutions.
    Please provide a solution for the following task:
    {task}"""
    return llm_agent(prompt)

def orchestrator_workflow(main_task: str) -> str:
    """
    Orchestrator that coordinates two workers to complete a task.
    1. Orchestrator breaks down the task
    2. Delegates to workers
    3. Synthesizes results
    """
    print("\n=== ORCHESTRATOR BREAKING DOWN TASK ===")
    orchestrator_prompt = f"""You are the Orchestrator. Your job is to break down this task into two subtasks 
    that can be handled by separate workers. Format your response as two clearly separated subtasks.
    
    Main task: {main_task}
    
    Respond in the following format:
    Subtask 1: [first subtask description]
    Subtask 2: [second subtask description]"""
    
    # Get subtasks from orchestrator
    subtasks_response = llm_agent(orchestrator_prompt)
    print(f"Orchestrator's task breakdown:\n{subtasks_response}\n")
    
    # Parse subtasks (assuming format is followed)
    subtask1 = subtasks_response.split("Subtask 1:")[1].split("Subtask 2:")[0].strip()
    subtask2 = subtasks_response.split("Subtask 2:")[1].strip()
    
    # Delegate to workers
    print("=== WORKER 1 RESPONSE ===")
    worker1_result = worker_1(subtask1)
    print(f"Worker 1 output:\n{worker1_result}\n")
    
    print("=== WORKER 2 RESPONSE ===")
    worker2_result = worker_2(subtask2)
    print(f"Worker 2 output:\n{worker2_result}\n")
    
    print("=== FINAL ORCHESTRATOR SYNTHESIS ===")
    # Final synthesis by orchestrator
    final_prompt = f"""As the Orchestrator, synthesize these two worker results into a final, coherent response:
    
    Worker 1 result: {worker1_result}
    Worker 2 result: {worker2_result}
    
    Provide a unified solution that incorporates both workers' insights."""
    
    final_result = llm_agent(final_prompt)
    print(f"Final synthesized response:\n{final_result}\n")
    
    return final_result

# Example usage:
print("=== STARTING WORKFLOW ===")
result = orchestrator_workflow("Analyze the impact of AI on healthcare and provide recommendations for implementation")

