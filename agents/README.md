#### Agent Frameworks

### intro

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/8u8XVB1W7xXWXn.png)
message queue \(python list of multi-turn conversation\) is formatted into string prompt using chat template

- _A Base Model_ is trained on raw text data to predict the next token.
- An _Instruct Model_ is fine-tuned specifically to follow instructions and engage in conversations

One just predicts the next word. The other has been 'fine-tuned' to predict the next word in a conversation between a user and a helpful assistant.

So using the regular model, "write me a poem" might be followed by "sure thing, I'll do it tomorrow\!" and in the instruct model, it will be followed by a poem.

Or just as easily, If you write 5 questions and hand it off to the base model, it will continue the pattern, and write... 5 more questions. The instruct model will answer them.

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/nessUaDmm8yKc.png)
basically different models have different chat templates because the special tokens can vary  
It’s important to note that a base model could be fine-tuned on different chat templates, so when we’re using an instruct model we need to make sure we’re using the correct chat template.

\_\_\_

Recent models like **Deepseek R1** or **OpenAI’s o1** were fine-tuned to _think before answering_. They use structured tokens like `<think>` and `</think>` to explicitly separate the reasoning phase from the final answer.

Unlike ReAct or CoT — which are prompting strategies — this is a **training-level technique**, where the model learns to think via examples.

General standard is llm generates tool needed in json format which is then executed, but also approach is llm writes the code which has that actions that need to be taken and then this code is executed \(Codeagents\)

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/CQTVxrN3jA9Zmn.png)
---
### Agent Types and Agentic Frameworks

CodeAgents, Toolcalling, preexisting import tools with library, agentic retrival, multiagent, vision and browser agents

### smolagents

 focuses on tool calls in code, simplifying the execution process. This is because there’s no need to parse the JSON in order to build code that calls the tools: the output can be executed directly.

rest all stuff is in notebook 

agentic rag- query formation, retrieval, evaluation of retrieval etc is given as a functionality tool to the agent  
can also have like vision and browing capability \(using selenium etc\)

### llamaindex

function calling vs react architectures

FC is usually a capability given by llm providers directly \(where we pass tool json schema as parameter\) basically the output here will be the tool call, but in a formal structured json object \(fixed format\) which is better than us prompting the llm to return a json response, Highly reliable, deterministic parsing. Because it cuts out conversational filler\)

but anyways if using fc, we have to parse the response and execute the tool call which it had said, similar to what we do in general agentic thing where tool is exectured and response is given to llm  
the advantage of tool calling is that's how the model was trained to do it and that's how it will work the best.

Modern frameworks like LangGraph by LangChain or LlamaIndex frequently merge these concepts. Developers often layer a **ReAct reasoning loop on top of a Function Calling engine**. This hybrid approach lets the LLM utilize native function calling to accurately trigger tools, while leveraging the ReAct loop framework to sequentially analyze the results and self-correct on the fly

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/4esGxnHqLSfbfj.png)
llamaindex gives easy abstractions to make agents having different tools, and to make multi agents where the root has agents as its tools type, and it will decide which to use, basically orchestrate the agents. where llama index gives us the abstraction over fc agent/react agent whenever we are building the smaaler ones which will be tools

below we have passed agent as a tool to a daddy agent

```
query\_agent = ReActAgent\(
    name="info\_lookup",
    description="Looks up information about XYZ",
    system\_prompt="Use your tool to query a RAG system",
    tools=\[query\_engine\_tool\],
    llm=llm
\)

\# Create and run the workflow
agent = AgentWorkflow\(
    agents=\[calculator\_agent, query\_agent\], root\_agent="calculator"
\)
```
agents stateless by default but can add context state so it remembers  
\_\_\_  
agentic workflows - tradeoff between independence vs behaviour control  
A workflow in LlamaIndex provides a structured way to organize your code into sequential and manageable steps - didnt read this much- skip

Agent tools can also modify the workflow state we mentioned earlier. Before starting the workflow, we can provide an initial state dict that will be available to all agents. The state is stored in the state key of the workflow context. It will be injected into the state\_prompt which augments each new user message.  
 basically here in context we can get and save any metrics or anywhing we want to be passed/bee in memory etc - example in notebook\(for example to keep count of function calls, we get the context state and have a key in the dictionary and increment it

```
async def add\(ctx: Context, a: int, b: int\) -> int:
    """Add two numbers."""
    \# update our count
    cur\_state = await ctx.store.get\("state"\)
    cur\_state\["num\_fn\_calls"\] \+= 1
    await ctx.store.set\("state", cur\_state\)

    return a \+ b
```
\_\_\_

https://academy.langchain.com/courses/intro-to-langgraph

### langGraph

for graph like workflows - to manage control flows 

 tradeoff between independence\(code agents\) vs behaviour control \(langgraph\)  


![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/FD2h6f7ZRmhYro.png)
3 main components - state, nodes, edges

**State** is the central concept in LangGraph. It represents all the information that flows through your application. The state is **User defined**, hence the fields should carefully be crafted to contain all data needed for decision-making process - like this we define 

```
from typing\_extensions import TypedDict

class egState\(TypedDict\):
    graph\_state: str
```
**Nodes** are python functions. Each node: Takes the state as input, Performs some operation, Returns updates to the state - here the nodes can contain llm calls, tool calls, conditions, input etc

**Edges** connect nodes and define the possible paths through your graph, these edges are basically a function only that returns which node to go to next, edge is mapped to the nodes in the state graph

The **StateGraph** is the container that holds your entire agent workflow: \(the State we defined above - the class basically we have to pass that name as argument to the graph builder

```
def decide\_mood\(state\) -> Literal\["node\_2", "node\_3"\]:
    \#some handling here, basically deciding what will be next node
    return "node\_3"
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

\# Build graph
builder = StateGraph\(egState\)
builder.add\_node\("node\_1", node\_1\)
builder.add\_node\("node\_2", node\_2\)
builder.add\_node\("node\_3", node\_3\)

\# Logic
builder.add\_edge\(START, "node\_1"\)
builder.add\_conditional\_edges\("node\_1", decide\_mood\)
builder.add\_edge\("node\_2", END\)
builder.add\_edge\("node\_3", END\)

\# Add
graph = builder.compile\(\)
```
here we can see added node1,2,3 to build and then to connect there is the logic where we set start to node 1 and then decide the branch

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/AeLbTqJTFiEo9C.png)
below, initial state we passed was the hi statement, and then in node 1 we appended “I am” and then we took a conditional egde to go to node 3 based on input/graph state etc to get the entire updated state at the end

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/BYUhtz8V5R1mHs.png)
lets say we need to route, here basically after classify email, route email is the routing function, if response from that function is spam then we take the handle span path after classify, if its legitimate we take the draft response step, using this add conditional edge statement we decidied the flow, we couldve also directly returned the exact node name so this mapping wouldnt have been necessary

```
email\_graph.add\_conditional\_edges\(
    "classify\_email",
    route\_email,
    \{
        "spam": "handle\_spam",
        "legitimate": "draft\_response"
    \}
\)
```
we can track the langgraph runs on langfuse — much helpful to keep execution track and input output checks etc, just need to initalize the langfuse handler callback and pass it as callback config to graph invokation and we can see all detailed logs on langfuse for everything in the graph — in IR project we had to add before every step separately because it was not a langgraph project

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/8tHGpzn6vkTYKi.png)
\_\_\_\_  
react agent in langgraph

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/6UPh3kPUNS9Bzb.png)
![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/3FmnkugiRhx7Hv.png)
assistant will loop over steps\(react reasoning act observe\) until it figures out the task and then ends, typically what we do in agentic systems.

But here we dont have to worry much about the conversation handling and all that like parsing llm output executing the tools sending its output and stuff all is taken care of  
  
using function calling here, to bind tools to llm \(augmenting the llm\), the graph will be one node assistant and a node of all tools where there is a cycle between the assistant node and the tools node \(the tools node is a special one given by langgraph\)

```
class AgentState\(TypedDict\):
    \# The document provided
    input\_file: Optional\[str\]  \# Contains file path \(PDF/PNG\)
    messages: Annotated\[list\[AnyMessage\], add\_messages\]
```
now here the ask will be agent state is This state is a little more complex than the previous ones we have seen. AnyMessage is a class from Langchain that defines messages, and add\_messages is an operator that adds the latest message rather than overwriting it with the latest state. 

 because its a react loop we want the previous history to be passed and add\_messages does that \(because react agent we need to send tool call output back to decide whether we wnat more iterations or not\) Maintain contextual awareness of previous interactions \(ensured by the operator add\_messages\)

\#build the graph, tools group doesnt need a function, we can just bundle it directly as seen then we add the conditonal edge from assitant to either tools or end and then a edge back from tools to assistant

---
### Agentic RAG

give rag as a tool to agent along with other agents \(so based on queries the correct tool can be used \(for eg web search, rag of part attendants information data, some apis as tools\)

\*in retriever - usually see if BM25\(sparse retrieval\) does the job  
best matching 25 - to find the most relevant documents by calculating a score based on term frequency \(TF\), inverse document frequency \(IDF\), and document length normalization. It is an improved, modern successor to TF-IDF that excels at finding exact matches and rare terms, typically used for initial search or as part of a \[Hybrid Search\] basically keyword search  
  
and only then move to vector database and advanced semantic search by using embedding models

---
### Fine tuning an LLM for Function Calling

The idea is, rather than relying only on prompt-based approaches, function calling trains your model to **take actions and interpret observations during the training phase**, making your AI more robust.

to-do : LoRa and Finetuning

in function calling, we add new roles to conversation - action and observation  
\(we are basically training the model to output something like <function/tool call> \(params\) xyz, this we do by giving some more special characters during fine tuning  


![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/tV43kbGPrGBuD.png)
https://docs.mistral.ai/studio-api/conversations/function-calling

For us its better to finetune the instruction tuned model rather than the base model as its easier because the base model just does next token prediction whereas the instruction tuned is finetuned to follow instructions/chat style vibe

example data for finetuning \(we need json\) here assisntant replies will contain the specialized tokens like <function call> etc

```
\#openai chat formal jsonl
\{
  "messages": \[
    \{"role": "system", "content": "You are a helpful assistant with access to tools. ..."\},
    \{"role": "user", "content": "Get the stock price for Apple."\},
    \{"role": "assistant", "content": null, "tool\_calls": \[\{"name": "get\_stock\_price", "args": \{"ticker": "AAPL"\}\}\]\}
  \]
\}
```
to actually fine tune the instruction tuned model using the training data we need to know how to fine tune it  
\_\_  
**LoRa - Low Rank Adaptation of LLMs ****https://huggingface.co/learn/llm-course/chapter11/4?fw=pt**

in essence it reduces number of trainable parameters  
It works by **inserting a smaller number of new weights as an adapter into the model to train**. This makes training with LoRA much faster, memory-efficient, and produces smaller model weights \(a few hundred MBs\), which are easier to store and share.

LoRA works by adding pairs of rank decomposition matrices to Transformer layers, typically focusing on linear layers. During training, we will “freeze” the rest of the model and will only update the weights of those newly added adapters.

By doing so, the number of **parameters** that we need to train drops considerably as we only need to update the adapter’s weights.

During inference, the input is passed into the adapter and the base model, or these adapter weights can be merged with the base model, resulting in no additional latency overhead.

LoRA is particularly useful for adapting **large** language models to specific tasks or domains while keeping resource requirements manageable. This helps reduce the memory **required** to train a model.

\_\_

in practical when using, we pass tools \(specific schema\) to client chat completions, and the use the response to format the next message to the llm based on tool execution response as you can see below - so the llm doesnt execute the tool, we do that after parsing the llm output \(where it can give tool\_calls\)

```
\# 2. Describe the tool to the model using JSON Schema format
tools = \[
    \{
        "type": "function",
        "function": \{
            "name": "get\_current\_weather",
            "description": "Get the current weather for a given location",
            "parameters": \{
                "type": "object",
                "properties": \{
                    "location": \{
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    \},
                    "unit": \{"type": "string", "enum": \["celsius", "fahrenheit"\]\},
                \},
                "required": \["location"\],
            \},
        \},
    \}
\]

\# Create the initial conversation history
messages = \[\{"role": "user", "content": "What is the weather like in Tokyo right now?"\}\]

\# 3. First API Call: Send the prompt and the available tools to the model
response = client.chat.completions.create\(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool\_choice="auto"  \# Let the model decide if it needs the tool
\)

response\_message = response.choices\[0\].message
tool\_calls = response\_message.tool\_calls

\# 4. Handle the Tool Call
if tool\_calls:
    print\("The model decided to use a tool\!"\)
    
    \# Append the model's tool call request to the conversation history
    messages.append\(response\_message\)
    
    \# Process each tool call requested by the model \(Handles Parallel Tool Calling\)
    for tool\_call in tool\_calls:
        function\_name = tool\_call.function.name
        function\_args = json.loads\(tool\_call.function.arguments\)
        
        print\(f"Calling function '\{function\_name\}' with arguments: \{function\_args\}"\)
        
        if function\_name == "get\_current\_weather":
            \# Execute your local Python function
            tool\_output = get\_current\_weather\(
                location=function\_args.get\("location"\),
                unit=function\_args.get\("unit", "celsius"\)
            \)
            
            \# Append the function result to the chat history
            \# The 'tool\_call\_id' must exactly match the id sent by the model
            messages.append\(\{
                "role": "tool",
                "tool\_call\_id": tool\_call.id,
                "name": function\_name,
                "content": tool\_output
            \}\)
              

```
---
### Agent Observability and Evaluation

needed for tracking, resource management, costs, issues, performance optimization, evaluation and feedback

- **Instrument Your Agent:**integrate observability tools via OpenTelemetry with the _smolagents_ framework.
- **Monitor Metrics:** Track performance indicators such as token usage \(costs\), latency, and error traces.
- **Evaluate in Real-Time:** Understand techniques for live evaluation, including gathering user feedback and leveraging an LLM-as-a-judge.
- **Offline Analysis:** Use benchmark datasets \(e.g., GSM8K\) to test and compare agent performance.

many agent frameworks such as [smolagents](https://huggingface.co/docs/smolagents/v1.12.0/en/index) use the [OpenTelemetry](https://opentelemetry.io/docs/) standard to expose metadata to the observability too

Langfuse - great tool for observability  
**Traces** represent a complete agent task from start to finish \(like handling a user query\).  
**Spans** are individual steps within the trace \(like calling a language model or retrieving data\).

Key metrics -  Latency, Costs, Requests errors, user feedback, accuracy

**Evaluation**

Online\(on real scenarios\), Offline \(on test data sets\)  
Langfuse has llm as a judge evaluation template, where we can set the judge to run everytime main logic runs and the trace is seen in langfuse, 

![](https://whimuc.com/BSh75h1yihfsuawoPtLmak/Cw5ouTiSMxbNoK.png)
previously we saw how to connect langfuse to langgraph, using the lg callback while invoking the graph

---
### Agents in games https://huggingface.co/learn/ml-games-course/unit0/introduction

using llms in games make it more interesting instead of harcoding interactions with NPCs, using llms it can become more dynamic and fun

currently integrating agents into games is less feasible because games are high speed at high fps and agents have the think act observe loop which can be time consuming, so for turn based games its good \(like pokemon\)

[https://huggingface.co/learn/agents-course/bonus-unit3/building\_your\_pokemon\_agent](https://huggingface.co/learn/agents-course/bonus-unit3/building_your_pokemon_agent)

this is cool, lets come back here later to do some handson




