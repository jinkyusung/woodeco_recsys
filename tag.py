import os
import pandas as pd
import requests
from dotenv import load_dotenv
import openai
from openai import OpenAI
from tqdm import tqdm
import re

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수에서 API 키들 불러오기
naver_client_id = os.getenv('NAVER_CLIENT_ID')
naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
openai_api_key = os.getenv('OPENAI_API_KEY')

categories = ['cafe', 'culture', 'food', 'landmark']

def get_prompt_for_category(category):
    # 카테고리에 따라 태그 생성 프롬프트를 다르게 설정?
    prompts = {
        'cafe': "Generate concise hashtags focused on the cafe's atmosphere, popular drinks, and customer experience. Example tags might include #cozy, #artisanCoffee, #freeWifi, #studySpot.",
        'culture': "Generate concise hashtags focused on the cultural site's exhibitions, facilities, and visitor impressions. Example tags might include #modernArt, #interactiveExhibit, #familyFriendly, #culturalHeritage.",
        'food': "Generate concise hashtags focused on the restaurant's cuisine, ambiance, and popular dishes. Example tags might include #gourmet, #localCuisine, #romanticSetting, #chefSpecial.",
        'landmark': "Generate concise hashtags focused on the landmark's historical significance, visitor experience, and photo opportunities. Example tags might include #mustSee, #historicalLandmark, #breathtakingViews, #touristFavorite."
    }
    return prompts[category]

def extract_tags_from_text(tag_string):
    tags = re.findall(r'#(\w+)', tag_string)
    return tags

def extract_district(address):
    parts = address.split()
    district = next((part for part in parts if '동' in part), None)
    return district

def naver_search(place, client_id, client_secret):
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    district = extract_district(place['address_name'])
    query = district + " " + place['place_name']

    params = {'query': query, 'display': 10}
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None

def generate_tags_with_gpt4(description, openai_api_key):
    client = OpenAI(
        api_key=openai_api_key,
    )
    prompt = "Generate a concise list of hashtags focused on the atmosphere, mood, design, and unique characteristics of the following place, avoiding specific food or cuisine types. Format each tag as '#word' in English. Example tags might include #cozy, #modern, #familyFriendly, #withOutdoorSeating, #romantic, #scenicView, #lively, #quiet, #historic:"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": description}
        ]
    )
    return response.choices[0].message.content

def process_places(file_path, output_path, naver_client_id, naver_client_secret, openai_api_key):
    places = pd.read_csv(file_path)
    results = []

    for index, place in tqdm(places[:20].iterrows(), total=20):
        search_results = naver_search(place, naver_client_id, naver_client_secret)
        if search_results and 'items' in search_results and search_results['items']:
            descriptions = []
            for item in search_results['items']:
                item_desc = item.get('description', '').strip()
                if item_desc:
                    descriptions.append(f"{item['title']} {item_desc}")
                else:
                    descriptions.append(item['title'])

            description = ', '.join(descriptions).strip()

            if description:
                raw_tags = generate_tags_with_gpt4(description, openai_api_key)
                tags = ' '.join(extract_tags_from_text(raw_tags))
                results.append({'Place': place['place_name'], 'Tags': tags})
            else:
                results.append({'Place': place['place_name'], 'Tags': 'Description not available'})
        else:
            results.append({'Place': place['place_name'], 'Tags': 'No results found'}) # title에 대한 내용 or 식당이름 or local search 결과로 descrption을 재구성할 것 인지? 

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == '__main__':
    for category in categories:
        input_file = f'./data/raw_{category}.csv'
        output_file = f'./data/results_{category}.csv'
        process_places(input_file, output_file, naver_client_id, naver_client_secret, openai_api_key)