import asyncio
import os
from typing import Optional

import requests
import google.generativeai as genai
from nio import AsyncClient, MatrixRoom, RoomMessageText
import nio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Matrix credentials
MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER")
MATRIX_USER = os.getenv("MATRIX_USER")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD")

# OpenWeatherMap configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_LOCATION = os.getenv("WEATHER_LOCATION", "Eindhoven,The Netherlands")  # Default location
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

async def get_weather_advice(temp: float, conditions: str) -> str:
    """Get AI-generated advice based on weather conditions."""
    prompt = f"""Given the current weather conditions:
    - Temperature: {temp}°C
    - Conditions: {conditions}
    Provide a brief, friendly suggestion (max 2 sentences) on how to stay comfortable in these conditions. Focus on practical advice."""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Unable to generate weather advice at the moment."

async def get_weather(location: str) -> Optional[str]:
    """Get weather information for a specific location."""
    try:
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(WEATHER_BASE_URL, params=params)
        response.raise_for_status()
        
        weather_data = response.json()
        weather_desc = weather_data["weather"][0]["description"]
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        
        # Get AI advice based on weather conditions
        advice = await get_weather_advice(temp, weather_desc)
        
        return (f"Weather in {location}:\n"
                f"🌡️ Temperature: {temp}°C\n"
                f"💧 Humidity: {humidity}%\n"
                f"📝 Conditions: {weather_desc}\n\n"
                f"👋 Suggestion: {advice}")
    except Exception as e:
        return f"Error getting weather data: {str(e)}"

async def get_ai_response(prompt: str) -> str:
    """Get response from Gemini AI."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    """Callback for when a message is received."""
    if event.body.startswith("!weather"):
        # Extract location from command or use default
        parts = event.body.split(maxsplit=1)
        location = parts[1] if len(parts) > 1 else WEATHER_LOCATION
        
        weather_info = await get_weather(location)
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": weather_info}
        )
    
    elif event.body.startswith("!ask"):
        # Extract question from command
        parts = event.body.split(maxsplit=1)
        if len(parts) > 1:
            question = parts[1]
            response = await get_ai_response(question)
            await client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": response}
            )
        else:
            await client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": "Please provide a question after !ask"}
            )

async def main() -> None:
    """Main bot function."""
    global client
    
    # Remove quotes from environment variables if present
    matrix_homeserver = os.getenv("MATRIX_HOMESERVER", "").strip('"')
    matrix_user = os.getenv("MATRIX_USER", "").strip('"')
    matrix_password = os.getenv("MATRIX_PASSWORD", "").strip('"')
    weather_api_key = os.getenv("WEATHER_API_KEY", "").strip('"')
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip('"')

    if not all([matrix_homeserver, matrix_user, matrix_password, weather_api_key, gemini_api_key]):
        print("Error: Missing required environment variables!")
        return

    try:
        # Initialize the client
        client = AsyncClient(matrix_homeserver, matrix_user)
        client.add_event_callback(message_callback, RoomMessageText)

        print(f"Logging in as {matrix_user}...")
        response = await client.login(matrix_password)
        
        if isinstance(response, nio.responses.LoginError):
            print(f"Failed to log in: {response.message}")
            return

        print("Login successful!")
        
        # Sync loop with error handling
        while True:
            try:
                sync_response = await client.sync(timeout=30000)
                if isinstance(sync_response, nio.responses.SyncError):
                    print(f"Error during sync: {sync_response.message}")
                    await asyncio.sleep(5)  # Wait before retrying
                    continue
            except Exception as e:
                print(f"Error during sync: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
                continue

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
