import streamlit as st
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
import requests
import json

def get_current_weather(location):
    url = f'https://wttr.in/{location}?format=j1'

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception(f'wttr.in error: status {response.status_code}')

    try:
        data = response.json()

    except ValueError:
        raise Exception(f'Could not find a location named {location}')

    current = data['current_condition'][0]
    today = data['weather'][0]

    return {
    'location': location,
    'temperature': float(current['temp_F']),
    'feels_like': float(current['FeelsLikeF']),
    'description': current['weatherDesc'][0]['value'],
    'humidity': int(current['humidity']),
    'wind_speed': int(current['windspeedMiles']),
    'min_temperature': float(today['mintempF']),
    'max_temperature': float(today['maxtempF'])
}

#testing the function with two locations
#st.write(get_current_weather("Syracuse, NY"))
#st.write(get_current_weather("Lima, Peru"))

#tool to get the current weather for a location using the wttr.in API
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state or city and country."
                    }
                },
                "required": ["location"]
            }
        }
    }
]

st.title("Lab 5 - What to Wear Bot")

location = st.text_input(
    "Enter a city:",
    placeholder="Syracuse, NY"
)

if st.button("Get Recommendations"):
    if not location:
        location = "Syracuse, NY"

    messages = [
        {
            "role": "user",
            "content": f"What should I wear today in {location}?"
        }
    ]

# calling OpenAI and allowing it to request the weather tool
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]

        arguments = json.loads(tool_call.function.arguments)
        weather_location = arguments["location"]

        weather = get_current_weather(weather_location)

        final_messages = [
            {
                "role": "user",
                "content": f"""
                Here is the current weather information for {weather_location}:

                {json.dumps(weather)}

                Based on this weather, suggest appropriate clothes to wear today
                and outdoor activities that would be appropriate for the weather.

                Do not ask follow up questions. Just provide a recommendation based 
                on the weather information provided.
                """
            }
        ]

        final_response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=final_messages
        )

        recommendation = final_response.choices[0].message.content

        st.write(recommendation)