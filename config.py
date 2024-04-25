# Category Look-up Table
CATEGORY_GROUP_CODE = {
    '지하철역':'SW8',
    '문화시설':'CT1',
    '관광명소':'AT4',
    '음식점':'FD6',
    '카페':'CE7'
}

# Seoul API
URL = 'http://openapi.seoul.go.kr:8088'
LOCATION_CODE_TABLE = './location_code_table.xlsx'

# Model Routes
MODEL_NAME = "word2vec-google-news-300"
MODEL = './model/' + MODEL_NAME + '.model'
SCORE_CACHE = './cache/score_cache.pkl'
TRANSLATION_CACHE = './cache/translation_cache.pkl'

# Results
PLACE_WITH_TAG = './data/place_with_tag.csv'
PLACE_WITH_PREFERENCE = './data/place_with_preference.csv'
PLACE = './data/place.csv'
