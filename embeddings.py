import re
import pandas as pd

from gensim.models import KeyedVectors
import gensim.downloader as api

import utils
import config as C


def tokenize(string):
    string = string.replace(',', ' ').strip()
    return re.split(r'[^a-zA-Z]+', string)


def get_similarity(user_tag, words, cache, model):    
    embedding_vectors = []
    for word in tokenize(words):
        score = cache.get((user_tag, words))
        if (not score) and (user_tag in model.key_to_index) and (word in model.key_to_index):
            score = model.similarity(user_tag, word)
        else:
            score = -1
        embedding_vectors.append(score)
        cache[(user_tag, word)] = score
    return embedding_vectors


def get_embedding(user_tags, places, model):
    cache = utils.load_pickle(C.EMBEDDING_CACHE)
    for user_tag in tokenize(user_tags):
        places[user_tag] = places.apply(lambda row : get_similarity(user_tag, row['tags'], cache, model), axis=1)
    utils.save_pickle(cache, C.EMBEDDING_CACHE)
    return places


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
    places = pd.read_csv(C.PLACES_WITH_TAGS).drop(columns=not_use_cols)

    # Get embeddings for each rows
    places = get_embedding(user_tags, places, model)
    places.to_csv(C.EMBEDDING, index=False)

    print(places.info())
    print('Done')
