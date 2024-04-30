import pandas as pd
import random
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from tqdm import tqdm
import json 
import folium


# Load environment variables
load_dotenv()

# API keys from environment variables
naver_client_id = os.getenv('NAVER_CLIENT_ID')
naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
openai_api_key = os.getenv('OPENAI_API_KEY')

categories = ['cafe', 'culture', 'food', 'landmark']

def merge_and_clean_location_data(raw, results):
    # Change 'Place' in results to 'place_name' for consistent merging
    results = results.rename(columns={"Place": "place_name"})
    # Merge the two datasets on 'place_name'
    merged_data = pd.merge(raw, results, on='place_name', how='outer', suffixes=('', '_drop'))
    # Remove duplicate columns by dropping those ending with '_drop'
    merged_data = merged_data[[c for c in merged_data.columns if not c.endswith('_drop')]]
    # Convert to dictionary format for easier JSON-like access
    location_data = merged_data.to_dict(orient='records')
    return location_data

def random_selection(locations, max_items=10):
    # Randomly select up to max_items locations
    selected_locations = random.sample(locations, min(max_items, len(locations)))
    return selected_locations

def construct_prompt(user_features, location_data):
    prompt = f"""
    Develop a location recommendation system that generates an efficient and user-specific itinerary based on provided user features and detailed location data. The system should generate recommendations by analyzing key user preferences such as age and interests, and match these with appropriate location tags (e.g., cafes, cultural spots). Recommendations should optimize for minimal walking distances using the haversine distance formula and consider logical sequence and travel efficiency between locations. The output should clearly state why each location fits the user’s preferences, using concise and factual reasoning, and maintain a structured format where each part of the itinerary is clearly separated and independent unless otherwise required by the sequence of events. Recommendations should be limited to four main stops to ensure clarity and focus,

    "task_requirements": [
        "Base recommendations on user features (e.g., age, interests) and location tags.",
        "Include a clear and factual reasoning for each recommended location.",
        "Ensure each recommendation is concise and stands on its own.",
        "Limit recommendations to four main stops for clarity.",
        "Use haversine formula to calculate shortest routes between locations.",
        "Output format should allow easy access to coordinates with 'x' and 'y' keys."
    ],

    Example:
    INPUT: User features {{user_feature}} (include age, interests), Location data {{location_data}} (tags from respective categories).

    OUTPUT:
    {{
    "itinerary": [
    {{"time": "05:00 PM", "Category": "cafe", "location": "Starbucks Sinchon Ogeori", "x": 126.938632525943, "y": 37.5558801935214}},
    {{"time": "06:30 PM", "Category": "culture", "location": "CGV Sinchon Artreon", "x": 126.938632525943, "y": 37.5558801935214}},
    ...
    ],
    "reasoning": [
    {{"step": "Starbucks Sinchon Ogeori", "reason": "Matches user's age group and preferred casual meeting spot."}},
    {{"step": "CGV Sinchon Artreon", "reason": "Aligns with user's cinematic interests and available showtimes."}},
    ...
    ]
    }}
    """
    return prompt

def get_location_recommendations(user_features, location_data):
    client = OpenAI(
        api_key=openai_api_key,
    )
    prompt = construct_prompt(user_features, location_data)

    description = f"INPUT: User features {user_features}, Location data {location_data}"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": description}
        ]
    )
    return response.choices[0].message.content

def select_random_user_record(user_data):
    random_user = random.choice(user_data.index)  # Pick a random index
    user_features = user_data.iloc[random_user].to_dict()  # Convert the row to a dictionary
    return user_features

# Load data from files
raw_cafes = pd.read_csv('./data/raw_cafe.csv')
cafes = pd.read_csv('./data/results_cafe.csv')
raw_culture = pd.read_csv('./data/raw_culture.csv')
culture = pd.read_csv('./data/results_culture.csv')
raw_food = pd.read_csv('./data/raw_food.csv')
food = pd.read_csv('./data/results_food.csv')
raw_landmarks = pd.read_csv('./data/raw_landmark.csv')
landmarks = pd.read_csv('./data/results_landmark.csv')

# Apply the function to all categories
merged_cafes = merge_and_clean_location_data(raw_cafes, cafes)
merged_culture = merge_and_clean_location_data(raw_culture, culture)
merged_food = merge_and_clean_location_data(raw_food, food)
merged_landmarks = merge_and_clean_location_data(raw_landmarks, landmarks)

user_data = pd.read_csv('./data/User_Data.csv')

results = []


selected_cafes = random_selection(merged_cafes)
selected_culture = random_selection(merged_culture)
selected_food = random_selection(merged_food)
selected_landmarks = random_selection(merged_landmarks)

location_data = {
    "cafes": selected_cafes,
    "culture": selected_culture,
    "food": selected_food,
    "landmarks": selected_landmarks
}

user_features = select_random_user_record(user_data)
user_features['Date Start Time'] = '17:00'
user_features['Date End Time'] = '22:00'
user_features['x'] = 37.555198169366435
user_features['y'] = 126.93698075993808
recommendations = get_location_recommendations(user_features, location_data)
recommendations_dict = json.loads(recommendations)
try:
    recommendations_dict = json.loads(recommendations)
except json.JSONDecodeError as e:
    print("JSON decoding 실패:", e)
    exit()

results.append({
    "user": user_features,
    "recommendations": recommendations
})

# map에 그리기 
# Define a list of colors for different categories
category_colors = {
    "cafe": "blue",
    "culture": "green",
    "food": "red",
    "landmarks": "purple"
}

# Create the map centered around the general area of the recommendations
m = folium.Map(location=[37.555198169366435, 126.93698075993808], zoom_start=15)

# 각 위치를 회색 마커로 추가
for category, places in location_data.items():
    for place in places:
        folium.Marker(
            location=[place['y'], place['x']],
            icon=folium.Icon(color='gray'),
            popup=f"{place['place_name']} ({place['category_group_name']})"
        ).add_to(m)
        
# Add markers and lines to the map
previous_coords = None
for item in recommendations_dict['itinerary']:
    coords = [item['y'], item['x']]
    category = item['Category']
    
    # Add marker
    folium.Marker(
        location=coords,
        popup=f"{item['time']} - {item['location']}",
        icon=folium.Icon(color=category_colors[category])
    ).add_to(m)
    
    # Add line to connect the locations if it's not the first location
    if previous_coords:
        folium.PolyLine(locations=[previous_coords, coords], color=category_colors[category]).add_to(m)
    
    # Update previous_coords to current
    previous_coords = coords

# Save the map
m.save('path_map.html')