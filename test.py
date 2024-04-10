from typing import Tuple
from pprint import pprint

from PyKakao import Local
import config as C

################ API Keys ################
import os
from dotenv import load_dotenv

load_dotenv()
REST_API = os.getenv("REST_API")
##########################################

        	
def get_current_coordinates(local, keyword: str, dataframe: bool = True) -> Tuple[str, str]:
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
    
    return x, y


if __name__ == '__main__':
    LOCAL = Local(service_key=REST_API)
    curr_x, curr_y = get_current_coordinates(LOCAL, '서강')

    code = C.CATEGORY_GROUP_CODE['음식점']
    location = LOCAL.search_category(code, dataframe=True, x=curr_x, y=curr_y, sort='distance')
    
    location.to_csv('location.csv', index=False)
    pprint('Done')
