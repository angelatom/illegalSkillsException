import json
import requests
from random import randint

#key = open("../keys/quotes_key.txt", "r").read()

def get_random_quote():
    URL_STUB = "https://favqs.com/api/quotes/"
    rand_num = str(randint(4,20))
    URL = URL_STUB + rand_num
    print(URL)
    r = requests.get(URL, headers={"Authorization": "Token token=941d1bc3cd831d275881fc9c87f04382","Content-Type": "application/json"})
    #print(response)
    #print(response.content)
    #return response
    #data = response
    #return data
    data = r.json()
   
    return data["body"]

print(get_random_quote())
