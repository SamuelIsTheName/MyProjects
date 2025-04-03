# Matrix Weather Bot

A simple Matrix bot that provides weather information for specified locations.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get your API credentials:
   - Sign up for a free API key at [OpenWeatherMap](https://openweathermap.org/api)
   - Have your Matrix.org account credentials ready

3. Create a `.env` file:
   - Copy `.env.example` to `.env`
   - Fill in your Matrix credentials and OpenWeatherMap API key

## Usage

1. Run the bot:
   ```
   python bot.py
   ```

2. In any Matrix room with the bot:
   - `!weather` - Get weather for the default location
   - `!weather London,UK` - Get weather for a specific location
   - `!ask` - Get answer to any question

## Features

- Provides temperature, humidity, and weather conditions
- Supports custom locations
- Responds to messages in any room the bot is in
- Provides answers to questions
