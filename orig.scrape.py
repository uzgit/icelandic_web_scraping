#!/usr/bin/python3

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas
import csv

from io import StringIO
import lxml.etree
import io
from PIL import Image
import time

def fa_ord_pre( row ):

    if(row["front"].isna()):
        fa_ord(row.front)

def fa_ord(word):

    print(f"looking up '{word}'")

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://bin.arnastofnun.is/leit/beygingarmynd/{word}")

    # is it ambiguous ?
    search_string  = f"//*[contains(text(), 'Smelltu')]"
    ambiguous = driver.find_elements(By.XPATH, search_string)
    if( len(ambiguous) > 0 ):
        possible_words = ambiguous[0].find_elements(By.XPATH, "../ul/li")
        
        print(f"The word '{word}' is ambiguous here. Please select from the list[{len(possible_words)}]:")
        for i in range(len(possible_words)):
            print(f"\t[{i+1}]: {possible_words[i].text}")

        print("Choose a word by number: ", end="")
        index = int(input()) - 1
        #index = 0

        print(f"Choosing [{index + 1}]: {possible_words[index].text}")
        word = possible_words[index].text.split(" ")[0]
        #print("Waiting for webpage to change...")
        possible_words[index].find_element(By.XPATH, "./b/a").click()

        #time.sleep(2)
        #current_url = driver.current_url
        #print(dir(EC))
        #print(current_url)
        #WebDriverWait(driver, 5).until_not(EC.url_matches(current_url))
        #print(f"Webpage changed {current_url} -> {driver.current_url} - proceeding...")
        WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[1]"))
                )

    element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[1]")

    part_of_speech = None
    gender = None
    flaschard_version = None
    
    classification = element.text

    if( "nafnorð" in classification ):
        
        part_of_speech = "nafnorð"
        gender = classification.replace("nafnorð", "")[:-1]
        
        search_string  = f"//*[contains(text(), 'Eintala')]"
        flashcard_version = driver.find_element(By.XPATH, search_string)
        flashcard_version = flashcard_version.find_element(By.XPATH, "../../../tbody/tr[1]/td[3]/span").text

        print(f"{flashcard_version} ({word}): {part_of_speech}, {gender}")
        print()

    return flashcard_version

def get_english(word):

    print(f"translating to english: '{word}'")

    options = Options()
    #options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(f"https://www.wordreference.com/isen/{word}")

    print("loaded webpage...")

    input()

    #search_string  = f"//*[contains(text(), 'Aðalþýðingar')]"
    #search_string  = f"//*[contains(text(), 'enska')]"
    search_string  = f"//*[normalize-space(text())='enska']"
    english_version = driver.find_element(By.XPATH, search_string)

    #for version in english_version:
    #    print(version.text)

    english_version = english_version.find_element(By.XPATH, "../../../tr[3]/td/strong").text

    print(f"definition: {english_version}")

    return english_version

def process( row ):
    front = fa_ord(row["word"])
    back  = get_english(row["front"])
    
    return front, back

#get_english("banani")

columns = ["initial_word", "front", "back"]
database = None
try:
    database = pandas.read_csv("database.csv", dtype=str)
except:
    database = pandas.DataFrame(columns=columns)

database = database.astype("string")

# add new words to the database
new_words = pandas.read_csv("new_words.csv")

new_database = pandas.concat([database, new_words])
new_database = new_database.drop_duplicates(subset="initial_word")
new_database = new_database.sort_values(by="front")
#new_database = new_database.fillna("")
print(new_database)

new_words["front"] = new_words.apply( lambda row: fa_ord(row),      axis=1 )
#new_words["back"]  = new_words.apply( lambda row: get_english(row.word), axis=1 )
#new_words[["front", "back"]] = new_words.apply( lambda row: process( row ), axis=1)

database = pandas.merge(database, new_words, on="front", how="outer")
database = database[columns]

database["initial_word"] = new_words["word"]
database["front"] = new_words["front"]
print(database)

database.to_csv("database.csv", index=False, quoting=csv.QUOTE_ALL)
