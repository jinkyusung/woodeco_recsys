import re
import pandas as pd

from gensim.models import KeyedVectors
import gensim.downloader as api

import utils
import config as C


def tokenize(string):
    string = string.replace(',', ' ').strip()
    return re.split(r'[^a-zA-Z]+', string)


def scoring(model, cache, user_tag, words):    
    score_vector = []
    for word in tokenize(words):
        score = cache.get((user_tag, words))
        if (not score) and (user_tag in model.key_to_index) and (word in model.key_to_index):
            score = model.similarity(user_tag, word)
        else:
            score = -1
        score_vector.append(score)
        cache[(user_tag, word)] = score
    return score_vector


def get_preference(model, places, user_tags):
    cache = utils.load_pickle(C.SCORE_CACHE)
    for user_tag in tokenize(user_tags):
        places[user_tag] = places.apply(lambda row : scoring(model, cache, user_tag, row['tags']), axis=1)
    utils.save_pickle(cache, C.SCORE_CACHE)
    return places


def category_simpler(category):
    return category.split('>')[1:]


if __name__=='__main__':

    # Load pre-trained embedding model.
    try:
        print(f'Try to load "{C.MODEL_NAME}"')
        model = KeyedVectors.load(C.MODEL)
    except:
        print(f'Download "{C.MODEL}"')
        model = api.load(C.MODEL_NAME)
        model.save(C.MODEL)
    print(f'Successfully load "{C.MODEL_NAME}"')

    # Load a list of places with tags
    user_tags = "cozy, cheep, walk, friend"
    not_use_cols = ['road_address_name','distance','id','phone','category_group_code','category_group_name','place_url']
    places = pd.read_csv(C.PLACE_WITH_TAG).drop(columns=not_use_cols)
    places['category'] = places.apply(lambda row: category_simpler(row['category_name']), axis=1)

    # Get preferences for each rows
    places = get_preference(model, places, user_tags)
    places.to_csv(C.PLACE_WITH_PREFERENCE, index=False)

    print(places.info())
    print('Done')
