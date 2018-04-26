import requests
import json
from pprint import pprint
from requests.auth import HTTPBasicAuth


def film_details_dictionary(film_dict_api):
    film_details = {}
    entity_list = ["planets", "starships", "vehicles", "species"]
    for entity in entity_list:
        entity_details = entity_details_dictionary(film_dict_api[entity], entity)
        film_details[entity] = entity_details
    characters_details = characters_details_dictionary(film_dict_api["characters"])
    film_details["title"] = film_dict_api["title"]
    film_details["director"] = film_dict_api["director"]
    film_details["producer"] = film_dict_api["producer"]
    film_details["release_date"] = film_dict_api["release_date"]
    film_details["characters"] = characters_details
    return film_details


def characters_details_dictionary(characters_url_list):
    characters_details = {}
    for character_url in characters_url_list:
        res = requests.get(character_url)
        character_dict = json.loads(res.content.decode())
        character_name = character_dict["name"]
        del character_dict["name"]
        del character_dict["films"]
        del character_dict["created"]
        del character_dict["edited"]
        del character_dict["url"]
        entity_details = entity_details_dictionary([character_dict["homeworld"]], "homeworld")
        character_dict["homeworld"] = entity_details
        entity_list = ["starships", "vehicles", "species"]
        for entity in entity_list:
            entity_details = entity_details_dictionary(character_dict[entity], entity)
            character_dict[entity] = entity_details
        characters_details[character_name] = character_dict
    return characters_details


def entity_details_dictionary(entity_list, name_of_entity):
    entity = {}
    for entity_url in entity_list:
        res = requests.get(entity_url)
        entity_dict = json.loads(res.content.decode())
        entity_name = entity_dict["name"]
        del entity_dict["name"]
        del entity_dict["films"]
        del entity_dict["created"]
        del entity_dict["edited"]
        del entity_dict["url"]
        if name_of_entity == "planets" or name_of_entity == "homeworld":
            del entity_dict["residents"]
        elif name_of_entity == "species":
            del entity_dict["people"]
            del entity_dict["homeworld"]
        else:
            del entity_dict["pilots"]
        entity[entity_name] = entity_dict
    return entity


def main():
    for index in range(1,8):
        print("Working on film {} ...".format(index))
        swapi_url = "https://swapi.co/api/films/{}/".format(index)
        response = requests.get(swapi_url)
        film_dict_api = json.loads(response.content.decode())
        film_details = film_details_dictionary(film_dict_api)
        film_details_str = json.dumps(film_details)

        url = "http://localhost:9200/star_wars_films/_doc/{}".format(index)
        # payload = '{}'.format()
        payload = film_details_str
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
            }
        auth_credentials = HTTPBasicAuth('elastic', 'tc7k85NeoZKOnTzKWIGx')

        response = requests.put(url, auth=auth_credentials, data=payload, headers=headers)
        s = json.loads(response.content.decode())
        print("=======================")
        pprint(s)
        print(".... Ingested")


if __name__ == "__main__":
    main()
