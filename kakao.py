import sys
import requests
import pandas as pd
from typing import Tuple

import folium
from folium.plugins import MiniMap
from PyKakao import Local

import utils
import config as C


sys.dont_write_bytecode = True

################ API Keys ################
import os
from dotenv import load_dotenv

load_dotenv()
REST_API = os.getenv("REST_API")
##########################################


def get_current_coordinates(local, keyword: str, dataframe: bool = True) -> Tuple[float, float]:
    """
    Develope을 위한 테스트 함수
    실제로는 User Device에서 현재 위치를 (x, y)로 받아온다.

    여기서는 개발의 용이성을 위해 
    query에 대해서 검색된 장소들 중에서 임의의 좌표 (x, y)를 반환한다.

    """
    if dataframe:
        result = local.search_keyword(keyword, dataframe)
        x = result.loc[0]['x']
        y = result.loc[0]['y']
    else:
        x = y = '0'
    return float(x), float(y)


def get_respones_from_search_category(group_code, page, roi, key):
    url = 'https://dapi.kakao.com/v2/local/search/category.json'
    params = {
        'category_group_code':group_code, 
        'page': page, 
        'rect': f"{','.join(map(str, roi))}"
    }
    headers = {"Authorization": "KakaoAK "+ key}
    return requests.get(url, params=params, headers=headers)


def search_in_patch(group_code, roi, key=REST_API):
    res = []
    page = 1
    
    while True:
        respones = get_respones_from_search_category(group_code, page, roi, key)
        
        _json = respones.json()
        is_end = _json['meta']['is_end']
        total_count = _json['meta']['total_count']

        if is_end:
            res += _json['documents']
            return res
        
        elif total_count > 45:
            x1, y1, x2, y2 = roi

            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            subroi1 = (x1, y1, mid_x, mid_y)
            subroi2 = (mid_x, y1, x2, mid_y)
            subroi3 = (x1, mid_y, mid_x, y2)
            subroi4 = (mid_x, mid_y, x2, y2)

            res += search_in_patch(group_code, subroi1, key=REST_API)
            res += search_in_patch(group_code, subroi2, key=REST_API)
            res += search_in_patch(group_code, subroi3, key=REST_API)
            res += search_in_patch(group_code, subroi4, key=REST_API)

            return res
        
        else:
            page += 1
            res += _json['documents']


def get_roi(curr_x: float, curr_y: float, distance: float) -> Tuple[float, float, float, float]:
    """
    curr_x   : RoI 중심점의 경도 값
    curr_y   : RoI 중심점의 위도 값
    distance : RoI의 가로, 세로 크기 (km)

    """
    dx = (distance / 88.74)
    dy = (distance / 109.958489129649955)
    
    x1  = curr_x - dx / 2
    y1  = curr_y - dy / 2

    x2 = x1 + dx
    y2 = y1 + dy

    return x1, y1, x2, y2


@utils.timer
def place_search_by_category(curr_x: float, curr_y: float, category: str, distance: float, key=REST_API) -> pd.DataFrame:
    """
    curr_x   : RoI 중심점의 경도 값
    curr_y   : RoI 중심점의 위도 값
    category : {'음식점', '카페', '지하철역', '문화시설', '관광명소'} 중 하나
    distance : RoI의 가로, 세로 크기 (km)

    """
    group_code = C.CATEGORY_GROUP_CODE[category]
    roi = get_roi(curr_x, curr_y, distance)

    searched = search_in_patch(group_code, roi, REST_API)
    df = pd.DataFrame()
    for row in searched:
        df_row = pd.DataFrame([row])
        df = pd.concat([df, df_row], ignore_index=True)
    return df


def make_map(curr_x, curr_y, df):
    m = folium.Map(location=[curr_y, curr_x], zoom_start=16)
    minimap = MiniMap() 
    m.add_child(minimap)
    for i in range(df.shape[0]):
        row = df.iloc[i]
        folium.Marker([row['y'], row['x']], tooltip=row['place_name'], popup=row['place_url']).add_to(m)
    folium.Marker([curr_y, curr_x], icon=folium.Icon(color='red'), tooltip='You', popup='You').add_to(m)
    return m


if __name__ == '__main__':
    LOCAL = Local(service_key=REST_API)
    curr_x, curr_y = get_current_coordinates(LOCAL, '신당')
    df = place_search_by_category(curr_x, curr_y, category='음식점', distance=0.8, key=REST_API)
    print(df.shape)
    df.to_csv('./data/foods.csv', index=False)

    m = make_map(curr_x, curr_y, df)
    m.save('./data/place_search.html')