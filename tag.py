import os
import pandas as pd
import requests
from dotenv import load_dotenv
import openai
from openai import OpenAI
from tqdm import tqdm
import re

# Load environment variables
load_dotenv()

# API keys from environment variables
naver_client_id = os.getenv('NAVER_CLIENT_ID')
naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
openai_api_key = os.getenv('OPENAI_API_KEY')

categories = ['cafe', 'culture', 'food', 'landmark']
# categories = ['food', 'landmark']

'''
# 아래 prompt가 더 좋을 수 있음 

def get_prompt_for_category(category, description):
    prompts = {
        'cafe': f"Generate unique hashtags in English capturing the special ambiance, community vibe, or any unique offerings of the cafe described as: {description}. Ignore descriptions that do not fit these characteristics. Encourage creative tags like #word: #cozy, #vintageDecor, #jazz, #petFriendly, #brunch.",
        'culture': f"Generate distinctive hashtags in English that highlight the cultural significance, unique exhibits, or the atmosphere of the venue described as: {description}. Ignore descriptions that do not fit these characteristics. Think of tags like #word: #modernart, #heritageSite, #interactiveArt, #movie, #theater.",
        'food': f"Generate appealing hashtags in English that describe the dining experience, unique flavors, or the atmosphere of the restaurant as described in: {description}. Ignore descriptions that do not fit these characteristics. Use imaginative tags #word: such as #fusionFlavors, #famous, #waiting, #highball, #chicDecor.",
        'landmark': f"Generate impactful hashtags in English that convey the historical importance, architectural uniqueness, or the experience of visiting the landmark detailed in: {description}. Ignore descriptions that do not fit these characteristics. Tags could include #word: #timeCapsule, #panoramicViews, #busking, #music."
    }
    return prompts[category]

# naver_search도 여러개의 query를 사용해 반환 받은 description을 사용하는 게 더 좋은 태그 생성에 도움이 될 수 있음음
'''


def get_prompt_for_category(category, description):
    # Define prompts for each category incorporating the provided description
    prompts = {
        'cafe': f"Generate concise hashtags based on the cafe's ambiance, popular drinks, and customer experience described as: {description}. Format each tag as '#word' in English. Suggested tags might include #cozy, #artisanCoffee, #freeWifi, #studySpot.",
        'culture': f"Generate concise hashtags based on the cultural site's exhibitions, facilities, and the impressions described as: {description}. Format each tag as '#word' in English. Suggested tags might include #modernArt, #interactiveExhibit, #familyFriendly, #culturalHeritage.",
        'food': f"Generate concise hashtags based on the restaurant's cuisine, ambiance, and the popular dishes described as: {description}. Format each tag as '#word' in English. Suggested tags might include #gourmet, #localCuisine, #romanticSetting, #chefSpecial.",
        'landmark': f"Generate concise hashtags based on the landmark's historical significance, visitor experiences, and photo opportunities described as: {description}. Format each tag as '#word' in English. Suggested tags might include #mustSee, #historicalLandmark, #breathtakingViews, #touristFavorite."
    }
    return prompts[category]

def extract_tags_from_text(tag_string):
    # Extract hashtags from a given string
    tags = re.findall(r'#(\w+)', tag_string)
    return tags

def extract_district(address):
    # Extract the district from an address
    parts = address.split()
    district = next((part for part in parts if '동' in part), None)
    return district

def naver_search(place, category, client_id, client_secret):
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    district = extract_district(place['address_name'])

    if category == 'food':
        query = f"{district} {place['place_name']} 음식점"
    elif category == 'culture':
        query = f"{district} {place['place_name']} 문화시설"
    elif category == 'cafe':
        query = f"{district} {place['place_name']} 카페"
    elif category == 'landmark':
        query = f"{district} {place['place_name']}"

        # Using both local and encyclopedia endpoints for landmarks
        local_url = "https://openapi.naver.com/v1/search/local.json"
        encyc_url = "https://openapi.naver.com/v1/search/encyc.json"
        params = {'query': query, 'display': 10}

        local_response = requests.get(local_url, headers=headers, params=params)
        encyc_response = requests.get(encyc_url, headers=headers, params=params)
        description = []

        if local_response.status_code == 200:
            local_results = local_response.json()['items']
            for item in local_results:
                description.append(f"{item['title']} {item['category']}")

        if encyc_response.status_code == 200:
            encyc_results = encyc_response.json()['items']
            for item in encyc_results:
                description.append(f"{item['title']} {item['description']}")

        return ', '.join(description)

    # Default to using local and blog searches for non-landmark categories
    blog_url = "https://openapi.naver.com/v1/search/blog.json"
    local_url = "https://openapi.naver.com/v1/search/local.json"
    params = {'query': query, 'display': 10}

    blog_response = requests.get(blog_url, headers=headers, params=params)
    local_response = requests.get(local_url, headers=headers, params=params)
    description = []

    if blog_response.status_code == 200:
        blog_results = blog_response.json()['items']
        for item in blog_results:
            description.append(f"{item['title']} {item['description']}")
    
    if local_response.status_code == 200:
        local_results = local_response.json()['items']
        for item in local_results:
            description.append(f"{item['title']} {item['category']}")
    
    return ', '.join(description)

def generate_tags_with_gpt4(description, openai_api_key, prompt):
    client = OpenAI(
        api_key=openai_api_key,
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": description}
        ]
    )
    return response.choices[0].message.content

def process_places(input_file, output_file, naver_client_id, naver_client_secret, openai_api_key, category):
    places = pd.read_csv(input_file)
    results = []

    for index, place in tqdm(places.iterrows(), total=places.shape[0]):
        search_description = naver_search(place, category, naver_client_id, naver_client_secret)
        if search_description:
            prompt = get_prompt_for_category(category, search_description)
            raw_tags = generate_tags_with_gpt4(search_description, openai_api_key, prompt)
            tags = ' '.join(extract_tags_from_text(raw_tags))
            results.append({'Place': place['place_name'], 'Tags': tags})
        else:
            print(place['place_name'])
            results.append({'Place': place['place_name'], 'Tags': 'Description not available'})

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")

if __name__ == '__main__':
    for category in categories:
        input_file = f'./data/raw_{category}.csv'
        # output_file = f'./data/results_{category}.csv'
        output_file = f'./data/experiments_{category}.csv'
        process_places(input_file, output_file, naver_client_id, naver_client_secret, openai_api_key, category)
