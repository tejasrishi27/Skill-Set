import os
import sys
from datetime import datetime
import requests
from dotenv import load_load_env

# Load environment variables from .env file
load_dotenv()

# Configuration & Constants
NUTRITIONIX_URL = "https://app.100daysofpython.dev/v1/nutrition/natural/exercise"
SHEETY_URL = os.getenv("SHEETY_URL")

APP_ID = os.getenv("NUTRITIONIX_APP_ID")
API_KEY = os.getenv("NUTRITIONIX_API_KEY")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN")

# Verify configuration loaded correctly
if not all([APP_ID, API_KEY, SHEETY_TOKEN, SHEETY_URL]):
    print("Error: Missing environment variables in .env file.")
    sys.exit(1)


def get_exercise_data(user_query: str) -> dict:
    """Sends natural language query to Nutritionix to fetch structured exercise stats."""
    headers = {
        "Content-Type": "application/json",
        "x-app-id": APP_ID,
        "x-app-key": API_KEY
    }
    
    payload = {"query": user_query}
    
    print("Sending request to Nutritionix API...")
    try:
        response = requests.post(url=NUTRITIONIX_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()["exercises"][0]
        return {
            "name": data["name"],
            "calories": data["nf_calories"],
            "duration": data["duration_min"]
        }
    except Exception as e:
        print(f"Unable to access data from Nutritionix API: {e}")
        return {}


def add_row_to_sheet(date_str: str, exercise: str, calories: float, duration: float) -> dict:
    """Appends workout tracking data into Google Sheets via Sheety."""
    headers = {
        "Authorization": f"Bearer {SHEETY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "sheet1": {
            "date": date_str,
            "exercise": exercise,
            "calories": calories,
            "duration": duration
        }
    }
    
    print("Sending data to Google Sheets...")
    try:
        response = requests.post(url=SHEETY_URL, json=payload, headers=headers)
        print(f"Sheety status code: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"Failed to write to Google Sheets: {e}")
        return {}


def main():
    # 1. Get user input or use standard test string
    user_input = input("Tell me what exercise you did today? ") or "ran for 1 hour"
    
    # 2. Get today's formatted date
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    # 3. Fetch analytics from Nutritionix
    workout = get_exercise_data(user_input)
    
    if not workout:
        print("Could not process exercise. Exiting.")
        return

    # 4. Save metrics into Google Sheets
    add_row_to_sheet(
        date_str=current_date,
        exercise=workout["name"],
        calories=workout["calories"],
        duration=workout["duration"]
    )


if __name__ == "__main__":
    main()
