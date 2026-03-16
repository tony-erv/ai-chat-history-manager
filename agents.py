import os, json, math
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS
import requests
from datetime import datetime
import pytz

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
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key is missing. Please set it in the .env file."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city, 
        "appid": api_key, 
        "units": "metric",
        "lang": "en"
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        return f"Current weather in {city}: {weather}, with a temperature of {temp}°C"
    except requests.exceptions.RequestException as e:
        return f"Network error fetching weather data: {e}"
    except Exception as e:
        return f"Error fetching weather for {city}: {e}"
    
def get_time(city):
    """Get the current time in a specified city."""
    username = os.getenv("GEONAMES_USERNAME")
    if not username:
        return "Error: GeoNames username is missing. Please set it in the .env file."
    
    search_url = "http://api.geonames.org/searchJSON"
    search_params = {
        "q": city,
        "maxRows": 1,
        "username": username
    }

    try:
        search_res = requests.get(search_url, params=search_params, timeout=5)
        search_res.raise_for_status()
        search_data = search_res.json()

        if not search_data["geonames"]:
            return f"City '{city}' not found."
        
        lat = search_data["geonames"][0]["lat"]
        lng = search_data["geonames"][0]["lng"]     

        tz_url = "http://api.geonames.org/timezoneJSON"
        tz_params = {
            "lat": lat,
            "lng": lng,
            "username": username
        }
        tz_res = requests.get(tz_url, params=tz_params, timeout=5)
        tz_res.raise_for_status()
        tz_data = tz_res.json()
        tz_id = tz_data.get("timezoneId")
        if not tz_id:
            return f"Could not determine timezone for {city}."  
        
        tz = pytz.timezone(tz_id)
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"Current time in {city} is {current_time}."
    
    except requests.exceptions.RequestException as e:
        return f"Network error fetching time data: {e}"
    except Exception as e:
        return f"Error fetching time for {city}: {e}"
    

TOOL_MAP = {
    "search_web": search_web,
    "calculate": calculate,
    "get_weather": get_weather,
    "get_time": get_time,
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
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time in the specified city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to get the current time for, e.g. 'New York' or 'Tokyo'."
                    }
                },
                "required": ["city"]
            }
        }
    }
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
        "Время в Керчи сейчас",
    ]

    for task in tasks:
        print(f"\nTask: {task}")
        answer, log = run_agent(task)
        print(f"Answer: {answer}")
        print("Steps Log:")
        for step in log:
            print(step)