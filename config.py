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
SCORE_CACHE = './cache/score.cache'
TRANSLATION_CACHE = './cache/translation.cache'

# Results
PLACE_WITH_TAG = './data/place_with_tag.csv'
PLACE_WITH_PREFERENCE = './data/place_with_preference.csv'
PLACE = './data/place.csv'

RAW_FOOD = './data/raw_food.csv'
RAW_CAFE = './data/raw_cafe.csv'
RAW_CULTURE = './data/raw_culture.csv'
RAW_LANDMARK = './data/raw_landmark.csv'

FOOD = './data/food.csv'
CAFE = './data/cafe_user.csv'
CULTURE = './data/culture.csv'
LANDMARK = './data/landmark.csv'
