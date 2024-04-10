import requests
import pandas as pd

import warnings
import config as C
from utils import timer


def url_generator(key: str, type: str, service: str, start_idx: int, end_index: int, area_nm: str) -> str:
    """
    KEY         | String  | 인증키 OpenAPI 에서 발급된 인증키
    TYPE        | String  | 요청파일타입
    SERVICE     | String  | 서비스명
    START_INDEX | INTEGER | 요청시작위치 (페이징 시작번호 입니다 : 데이터 행 시작번호)
    END_INDEX   | INTEGER | 요청종료위치 (페이징 끝번호 입니다 : 데이터 행 끝번호)
    AREA_NM     | STRING  | 핫스팟 장소명, 장소명 or 장소코드 입력 (참고: location_code_table.xlsx)
    """
    urls = [C.SEOUL_API, key, type, service, str(start_idx), str(end_index), area_nm]
    url = '/'.join(urls)
    return url


def get_area_cd(area_nm: str) -> str:
    table = pd.read_excel(C.LOCATION_CODE_TABLE)
    filtered = table[table['AREA_NM'].str.contains(area_nm, case=False, regex=True)]
    return filtered[['AREA_CD', 'AREA_NM']].reset_index(drop=True)


@timer
def get(url):
    return requests.get(url)


warnings.filterwarnings("ignore", category=UserWarning)
url = url_generator(C.KEY, 'json', 'citydata', 1, 5, '광화문·덕수궁')

response = get(url)
data = response.json()
print(get_area_cd('수궁'))