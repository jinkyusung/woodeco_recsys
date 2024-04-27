import requests
import time

################ API Keys ################
import os
from dotenv import load_dotenv

load_dotenv()
SK_OPEN_API_KEY = os.getenv("SK_OPEN_API_KEY")
##########################################

def get_walk_route_duration(locs: list) -> list:
    """
    Tmap api를 사용해 주어진 위치 목록(locs)을 바탕으로 각 위치 간의 도보 소요 시간 계산

    Parameters:
    locs (list): 위치 데이터를 포함하는 2차원 list, 각 원소는 [x좌표, y좌표, 장소명] 형식

    Returns:
    list: 각 위치 쌍 간의 도보 소요 시간(초)을 담은 list. api 응답을 받지 못한 경우 -1 반환
    """

    # Tmap API URL, header
    url = 'https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'appKey': SK_OPEN_API_KEY
    }

    # 인접한 위치 쌍에 대한 도보 경로 저장할 리스트 초기화
    durations = [-1 for i in range(len(locs) - 1 )]

    # 인접한 위치 쌍에 대해 도보 경로 API 요청
    for i in range(len(locs) - 1 ):
        data = {
            "startX": locs[i][0],
            "startY": locs[i][1],
            "startName": locs[i][2],
            "endX": locs[i+1][0],
            "endY": locs[i+1][1],
            "endName": locs[i+1][2]
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response_data = response.json()
        
        # 응답 데이터에서 도보 소요 시간 추출
        if 'features' in response_data:
            sp_feature = response_data['features'][0]
            if 'properties' in sp_feature and 'totalTime' in sp_feature['properties']:
                durations[i] = sp_feature['properties']['totalTime']
    return durations

if __name__ == '__main__':
    # 테스트 데이터
    l = [
            [126.930562418509,37.5445456700197,"채선당 광흥창점"],
            [126.932433807492,37.5447954313915,"마미"],
            [126.930634805464,37.544581752529,"바드다드 카페"],
            [126.93408804803389,37.544929714208216,"김밥천국 신수사거리점"]
    ]
    start_time = time.time()
    print(f"도보 소요 시간(초): {get_walk_route_duration(l)}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    # 4개의 location 기준 1.9초정도 걸림
    print(f"Request 처리 시간: {elapsed_time:.2f}초")