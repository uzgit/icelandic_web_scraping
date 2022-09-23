#!/usr/bin/python3

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

def fa_ord(word):
   
    options = Options()
    #options.add_argument("--headless")
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
        possible_words[index].find_element(By.XPATH, "./b/a").click()

    current_url = driver.current_url
    WebDriverWait(driver, 5).until_not(EC.url_changes(current_url))
    #time.sleep(1)

    print(f"searching for {word}")
    #search_string  = f"//*[contains(text(), '{word} ')]"
    search_string  = f"//*[contains(text(), '{word}')]"

    classification = driver.find_element(By.XPATH, search_string)

    print(f"classification: {classification}")

    #time.sleep(10)

    part_of_speech = None
    gender = None
    flaschard_version = None

    if( "nafnorð" in classification ):
        
        part_of_speech = "nafnorð"
        gender = classification.replace("nafnorð", "")[:-1]
        
        search_string  = f"//*[contains(text(), 'Eintala')]"
        flashcard_version = driver.find_element(By.XPATH, search_string)
        flashcard_version = flashcard_version.find_element(By.XPATH, "../../../tbody/tr[1]/td[3]/span").text

    print(f"{flashcard_version} ({word}): {part_of_speech}, {gender}")

#fa_ord("hádegismat")
fa_ord("hundur")
fa_ord("banani")
fa_ord("kaka")
fa_ord("ostur")
fa_ord("safi")
fa_ord("fiskur")
