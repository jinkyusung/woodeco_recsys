import re
import pandas as pd
import json

from gensim.models import KeyedVectors
import gensim.downloader as api

import utils
import config as C

import urllib.request

################ API Keys ################
import os
from dotenv import load_dotenv

load_dotenv()
PAPAGO_ID = os.getenv("PAPAGO_ID")
PAPAGO_API = os.getenv("PAPAGO_API")
##########################################


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


def kor2eng(kor: str, translation_cache, client_id, client_secret):
    eng = translation_cache.get(kor)
    if not eng:
        encText = urllib.parse.quote(kor)
        data = "source=ko&target=en&text=" + encText
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
        request.add_header("X-NCP-APIGW-API-KEY", client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            eng = json.loads(response_body.decode('utf-8'))['message']['result']['translatedText']
            translation_cache[kor] = eng
    return eng


def category_simpler(category, place_name, translation_cache, client_id, client_secret):
    category = category.replace(' > ', ' ').replace(',', ' ').strip().split(' ')[1:]
    if category and place_name.find(category[-1]) > -1:
        category.pop()

    for i, kor in enumerate(category):
        category[i] = kor2eng(kor, translation_cache, client_id, client_secret)

    return category


if __name__=='__main__':

    # Load a list of places with tags
    not_use_cols = ['road_address_name','distance','id','phone','category_group_code','category_group_name','place_url']
    places = pd.read_csv(C.PLACE_WITH_TAG).drop(columns=not_use_cols)
    
    # Convert kor category_name to eng category_name
    translation_cache = utils.load_pickle(C.TRANSLATION_CACHE)
    places['category_name'] = places.apply(
        lambda row: category_simpler(row['category_name'], row['place_name'], translation_cache, PAPAGO_ID, PAPAGO_API), axis=1
    )
    utils.save_pickle(translation_cache, C.TRANSLATION_CACHE)
    print(f'Successfully load and update "{C.PLACE_WITH_TAG}"')

    # Get preferences for each rows
    try:
        print(f'Try to load "{C.MODEL_NAME}"')
        model = KeyedVectors.load(C.MODEL)
    except:
        print(f'Download "{C.MODEL}"')
        model = api.load(C.MODEL_NAME)
        model.save(C.MODEL)
    print(f'Successfully load "{C.MODEL_NAME}"')

    user_tags = "cozy, cheep, walk, friend"
    places = get_preference(model, places, user_tags)
    places.to_csv(C.PLACE, index=False)
    print(f'Done.')
