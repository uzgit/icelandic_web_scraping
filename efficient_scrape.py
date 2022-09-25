#!/usr/bin/python3

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from googletrans import Translator
import time
import pandas
import csv

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def page_is_loading(driver):
    while True:
        x = driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        else:
            yield False

def fa_ord(word, driver, database=None):

    print(f"looking up nominative with article for '{word}'")

    target_url = f"https://bin.arnastofnun.is/leit/beygingarmynd/{word}"

    current_url = driver.current_url
    print("getting target url")
    driver.get(target_url)
    print("did the get, now waiting...")

    time.sleep(1)

    search_string  = f"//*[contains(text(), '{word}')]"
    element = driver.find_element(By.XPATH, search_string)

    classification = ""
    try:
        element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[1]")
        classification = element.text
        print(f"\t\tfound {bcolors.OKGREEN}{classification}{bcolors.ENDC}")
    except:
        print(f"\t\tdid not find the element!")

    back = ""
    if( "fannst ekki" in classification ):
        back = ""
    if( "orð fundust. Smelltu á það orð sem þú vilt sjá" in classification ):
        back = ""
        print(f"{bcolors.FAIL}{classification}{bcolors.ENDC}")

    elif( "land eða landsvæði" in classification ):
        element = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[1]/h2")
        print(f"{bcolors.FAIL}{classification}{bcolors.ENDC}")
        
    elif( "nafnorð" in classification and "sérnafn" not in classification ):
        search_string  = f"//*[contains(text(), 'Eintala')]"
        flashcard_version = driver.find_element(By.XPATH, search_string)
        flashcard_version = flashcard_version.find_element(By.XPATH, "../../../tbody/tr[1]/td[3]/span").text
        base_noun = classification.split(" ")[0]

        back = f"{base_noun} ({flashcard_version})"
    
    elif( "sagnorð" in classification ):

        first_person_singular = ""
        infinitive = ""

        #first_person_singular = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[2]/div[5]/div[1]/table/tbody/tr[1]/td[2]/table/tbody/tr/td[2]/span").text
        second_person_singular = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[2]/div[5]/div[1]/table/tbody/tr[2]/td[2]/table/tbody/tr/td[2]/span").text

        infinitive = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[2]/div[2]/div/span").text

        back = f"að {infinitive} (þú {second_person_singular})"

    elif( "atviksorð" in classification ):

        back = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div/h2").text
        back = back.replace("atviksorð", "")[:-1]
    
    elif( "óákveðið fornafn" in classification ):
        element = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[2]/div[1]/div[2]/div/div[1]/div/div[1]/h2")
        back = element.text

    print(f"flashcard version: {bcolors.OKCYAN}{back}{bcolors.ENDC}")

    # incremental save
    database.to_csv("database.csv", index=False, quoting=csv.QUOTE_ALL)

    print("got past waiting")
    return back

def get_english(word):

    print(f"translating to english: '{word}'")

    translator = Translator()
    translation = translator.translate(word, src="is", dest="en").text

    print(f"found translation: {word} -> {translation}")

    return translation

def process( row, driver, translator ):

    front = ""
    if( pandas.isnull(row["front"]) ):
        front = fa_ord( row["initial_word"], driver )

    back = ""
    if( pandas.isnull(row["back"]) ):
        back = translator.translate(row.front, src="is", dest="en").text
    
    return front, back

####################################################################################################

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

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
translator = Translator()

# get nominative case of each word with the article
database["front"] = database.apply(lambda row: fa_ord(row.initial_word, driver, database) if(pandas.isnull(row.front)) else row.front, axis=1)
# incremental save
database.to_csv("database.csv", index=False, quoting=csv.QUOTE_ALL)

database["back"] = database.apply(lambda row: get_english(row.front) if(pandas.isnull(row.back)) else row.back, axis=1)
#database[["front", "back"]] = database.apply( lambda row: process(row, driver, translator) )
# incremental save
database.to_csv("database.csv", index=False, quoting=csv.QUOTE_ALL)

print("Total data:")
print(database)

flashcards = database[["front","back"]]
flashcards.to_csv("flashcards.txt", index=False, header=False, sep ='\t')
