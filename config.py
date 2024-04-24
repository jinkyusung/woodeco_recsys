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

# Embeddings Model Routes
EMBEDDING_CACHE = './models/embedding_cache.pkl'
MODEL_NAME = "word2vec-google-news-300"
MODEL = './models/' + MODEL_NAME + '.model'

# Embeddings Results
PLACES_WITH_TAGS = './data/tags.csv'
EMBEDDING = './data/embeddings.csv'
