#!/usr/bin/python3

import requests
from requests_html import HTMLSession


def fa_nafnfall_med_greini(word):
    
    global session
    base_url = "https://bin.arnastofnun.is/leit/beygingarmynd/"
    full_url = f"{base_url}/{word}"

    

    response = session.get( full_url )
    #response = response.html.render()

    return response

global session
session = HTMLSession()


response = fa_nafnfall_med_greini("banana")

print(response)
