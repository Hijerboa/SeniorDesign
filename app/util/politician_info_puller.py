import requests
from util.cred_handler import get_secret


def get_congress_members(congress: int, chamber: str):
  url = "https://api.propublica.org/congress/v1/{0}/{1}/members.json".format(str(congress), chamber)

  payload={}
  headers = {
    'X-API-Key': get_secret('pro_publica_api_key')
  }

  response = requests.request("GET", url, headers=headers, data=payload)

  print(response.text)