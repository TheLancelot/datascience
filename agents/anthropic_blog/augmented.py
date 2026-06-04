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

OPENWEATHER_API_KEY = os.environ['OPENWEATHER_API_KEY']

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = httpx.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp'], data['weather'][0]['description']
    else:
        raise Exception("Failed to retrieve weather data")

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature and weather description for a given city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city, e.g. London, New York"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

def openai_tool_call(city_name: str) -> str:
    completion = client_llm.chat.completions.create(
        model="llama-3-1-8b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that can get weather information for a specific city. Use the tool to get the weather information."},
            {"role": "user", "content": f"What's the weather like in {city_name} today?"}
        ],
        tools=tools
    )

    # Parse the tool call and execute the get_weather function
    tool_call = completion.choices[0].message.tool_calls[0]
    args = tool_call.function.arguments
    city = args['city']
    temperature, description = get_weather(city)

    # Final response incorporating the weather result
    final_completion = client_llm.chat.completions.create(
        model="llama-3-1-8b-instruct",
        messages=[
            {"role": "user", "content": f"What's the weather like in {city_name} today?"},
            completion.choices[0].message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": f"The current temperature in {city} is {temperature}°C with {description}."
            }
        ]
    )
    
    return final_completion.choices[0].message.content

result = openai_tool_call("Paris")
print(result)