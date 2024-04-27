import re
import json
from typing import List

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


def metric(score_vector: List[float], alpha=0.6) -> float:
    score_vector.sort(reverse=True)
    score = score_vector.pop()
    while score_vector:
        score = (1-alpha) * score + alpha * score_vector.pop()
    return score * 100


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

    return metric(score_vector)


def get_preference(model, places, user_tags):
    cache = utils.load_pickle(C.SCORE_CACHE)
    for user_tag in tokenize(user_tags):
        places[user_tag] = places.apply(lambda row : scoring(model, cache, user_tag, row['tags']), axis=1)
    places['preference'] = 0
    for user_tag in tokenize(user_tags):
        places['preference'] += places[user_tag]
        places = places.drop(columns=[user_tag])
    places['preference'] /= len(user_tags)
    utils.save_pickle(cache, C.SCORE_CACHE)
    return places


def kor2eng(kor: str, translation_cache, client_id, client_secret) -> str:
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
        category[i] = kor2eng(kor, translation_cache, client_id, client_secret).lower()

    return category


def column_rearrange(places):
    translation_cache = utils.load_pickle(C.TRANSLATION_CACHE)
    places.rename(columns={'y':'latitude', 'x':'longitude'}, inplace=True)
    places = places[['place_name','category_name','preference','latitude','longitude','address_name']]
    places.loc[:, 'category_name'] = places.apply(
        lambda row: category_simpler(row['category_name'], row['place_name'], translation_cache, PAPAGO_ID, PAPAGO_API), axis=1
    )
    utils.save_pickle(translation_cache, C.TRANSLATION_CACHE)
    return places