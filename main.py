import pandas as pd

from haversine import Unit
from haversine import haversine

# Embedding
from gensim.models import KeyedVectors
import gensim.downloader as api

# Custom
import config as C
import preprocess
import utils


################ API Keys ################
import os
from dotenv import load_dotenv

load_dotenv()
PAPAGO_ID = os.getenv("PAPAGO_ID")
PAPAGO_API = os.getenv("PAPAGO_API")
##########################################


def main():

    # Load Word2Vec Model
    try:
        print(f'Try to load "{C.MODEL_NAME}"')
        model = KeyedVectors.load(C.MODEL)
    except:
        print(f'Download "{C.MODEL}"')
        model = api.load(C.MODEL_NAME)
        model.save(C.MODEL)
    print(f'Successfully load "{C.MODEL_NAME}"')

    # Actual Service
    # lat, lon = current_coordinates_by_some_API(*args, **argv)
    # user_tag = get_user_tag(*args, **argv)

    # Debug
    lat = 37.555198169366435
    lon = 126.93698075993808
    user_tags = 'silent, comport, cheep'

    # Load Raw Data of Places
    raw_food = pd.read_csv(C.RAW_FOOD)
    # raw_cafe = pd.read_csv(C.RAW_CAFE)
    # raw_culture = pd.read_csv(C.RAW_CULTURE)
    # raw_landmark = pd.read_csv(C.RAW_LANDMARK)

    # Calculate interactions between `user_tag` and `place_tag`
    food = preprocess.get_preference(model, raw_food, user_tags)
    # cafe = preprocess.get_preference(model, raw_cafe, user_tags)
    # culture = preprocess.get_preference(model, raw_culture, user_tags)
    # landmark = preprocess.get_preference(model, raw_landmark, user_tags)

    # Load a list of places with tags
    food = preprocess.column_rearrange(food)

    food.to_csv(C.FOOD, index=False)
    # cafe.to_csv(C.CAFE, index=False)
    # culture.to_csv(C.CULTURE, index=False)
    # landmark.to_csv(C.LANDMARK, index=False)

    


if __name__ == '__main__':
    main()
