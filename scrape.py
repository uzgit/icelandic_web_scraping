#!/usr/bin/python3

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from googletrans import Translator

import pandas
import csv

def fa_ord(word):

    print(f"looking up nominative with article for '{word}'")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://bin.arnastofnun.is/leit/beygingarmynd/{word}")

    flashcard_version = None
    try:

        # is it ambiguous ?
        search_string  = f"//*[contains(text(), 'Smelltu')]"
        ambiguous = driver.find_elements(By.XPATH, search_string)
        if( len(ambiguous) > 0 ):
            possible_words = ambiguous[0].find_elements(By.XPATH, "../ul/li")

            print(f"The word '{word}' is ambiguous here. Please select from the list[{len(possible_words)}]:")
            for i in range(len(possible_words)):
                print(f"\t[{i+1}]: {possible_words[i].text}")

            print("Choose a word by number: ", end="")
            #index = int(input() or 1) - 1
            index = 0

            print(f"Choosing [{index + 1}]: {possible_words[index].text}")
            word = possible_words[index].text.split(" ")[0]
            possible_words[index].find_element(By.XPATH, "./b/a").click()

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
    except Exception as e:
        print(f"Exception while looking up {word}")
        print(e)

    return flashcard_version

def get_english(word):

    print(f"translating to english: '{word}'")

    translator = Translator()
    translation = translator.translate(word, src="is", dest="en").text

    print(f"found translation: {word} -> {translation}")

    return translation


#def get_english(word):
#
#    print(f"translating to english: '{word}'")
#
#    options = Options()
#    #options.add_argument("--headless")
#    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#
#    driver.get(f"https://www.wordreference.com/isen/{word}")
#    search_string  = f"//*[normalize-space(text())='enska']"
#
#    input()
#
#    english_version = ""
#    try:
#        english_version = driver.find_element(By.XPATH, search_string)
#        english_version = english_version.find_element(By.XPATH, "../../../tr[3]/td/strong").text
#        print(f"definition: {english_version}")
#    except:
#        print("did not find the word on the page...skipping")
#
#    return english_version

# get existing database, or create it if it doesn't exist
columns = ["initial_word", "front", "back"]
database = None
try:
    database = pandas.read_csv("database.csv", dtype=str)
except:
    database = pandas.DataFrame(columns=columns)
database = database.astype("string")

print("Current data:")
print(database)

# add new words to the database
new_words = pandas.read_csv("new_words_2.csv")
database = pandas.concat([database, new_words])
database = database.drop_duplicates(subset="initial_word")
database = database.sort_values(by="front")

print("With new words:")
print(database)

# get nominative case of each word with the article
database["front"] = database.apply(lambda row: fa_ord(row.initial_word) if(pandas.isnull(row.front)) else row.front, axis=1)
# incremental save
database.to_csv("database.csv", index=False, quoting=csv.QUOTE_ALL)

database["back"] = database.apply(lambda row: get_english(row.front) if(pandas.isnull(row.back)) else row.back, axis=1)
# incremental save
database.to_csv("database.csv", index=False, quoting=csv.QUOTE_ALL)

print("Total data:")
print(database)

flashcards = database[["front","back"]]
flashcards.to_csv("flashcards.txt", index=False, header=False, sep ='\t')
