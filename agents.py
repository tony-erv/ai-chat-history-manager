import os, json, math
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
max_steps = 5

def search_web(query):
    """Search the web using DuckDuckGo and return a summary of results."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    if not results:
        return "No results found."
    
    output = []
    for r in results[:3]:
        output.append(f"[{r['title']}]\n{r['body']}\n{r['href']}")
        return "\n\n".join(output) # Return only the top result for brevity

def calculate(expression):
    """Evaluate a mathematical expression safely."""
    try:
        # Only allow numbers, operators, and math functions
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")} 
        allowed.update({"__builtins__": {}})  # Disable built-in functions for safety
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"
    
def get_weather(city):
    """Mock function to get weather info for a city."""
    return f"The current weather in {city} is sunny with a temperature of 25°C."

TOOL_MAP = {
    "search_web": search_web,
    "calculate": calculate,
    "get_weather": get_weather,
}

TOOLS = [
    {
        "type":"function",
        "function":{
            "name": "search_web",
            "description": "Search the web for up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query. For example, 'What is the capital of France?' or 'Latest news on AI?'."
    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type":"function",
        "function":{ 
            "name": "calculate",
            "description": "Perform a calculation based on the provided expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to calculate, e.g. '2 + 2' or 'sqrt(16)'."
                    }
                },    
                "required": ["expression"]
            }
        }  
    },
    {
        "type":"function",
        "function":{
            "name": "get_weather",
            "description": "Retrieve current weather information for a specified city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to get weather information for, e.g. 'New York' or 'Tokyo'."
    }
                },
                "required": ["city"]
            }
        }
    },
]  

def run_agent(task, system_prompt="You are a helpful assistant that can perform various tasks using tools."):
    """Run an agent to complete a task using the defined tools."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task}
    ]
    steps_log = []

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        
        if not msg.tool_calls:
            steps_log.append({"step": "answer", "content": msg.content})
            return msg.content, steps_log
        
        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"  → {name}({args})")

            if name not in TOOL_MAP:
                result = f"Unknown tool: {name}"
            else:
                try:
                    result = TOOL_MAP[name](**args)
                except Exception as e:
                    result = f"Error executing tool {name}: {e}"
        
            messages.append({
                "role": "tool", 
                "tool_call_id": tool_call.id, 
                "content": str(result)
                })

            steps_log.append({"step": "name", "args": args, "result": result[:200]})  # Log tool name, args, and truncated result
        

    return "Sorry, I couldn't complete the task within the step limit.", steps_log

if __name__ == "__main__":
    tasks = [
        "погода в симферополе, Каире и Дублине сейчас"
    ]

    for task in tasks:
        print(f"\nTask: {task}")
        answer, log = run_agent(task)
        print(f"Answer: {answer}")
        print("Steps Log:")
        for step in log:
            print(step)