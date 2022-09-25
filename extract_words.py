#!/usr/bin/python3

import re
import PyPDF2

pages = []

# creating a pdf file object
pdf = open('textbook.pdf', 'rb')

# creating a pdf reader object
pdf_reader = PyPDF2.PdfFileReader(pdf)

# printing number of pages in pdf file
print(pdf_reader.numPages)

for page_number in range(pdf_reader.numPages):
    
    # creating a page object
    page = pdf_reader.getPage(page_number)

    # extracting text from page
    pages.append(page.extractText())

    print(page.extractText())
    print(f"page above: {page_number}")

# closing the pdf file object
pdf.close()

# clean up
#words = [ word.replace("\n", "") for word in words ]

print(pages)

acceptable_characters = "AÁBDÐEÉFGHIÍJKLMNOÓPRSTUÚVXYÝÞÆÖaábdðeéfghiíjklmnoóprstuúvxyýþæö \n"
sanitized_pages = []
for page in pages:

    sanitized_page = ""
    for letter in page:
        if letter in acceptable_characters:
            sanitized_page += letter

    sanitized_page = re.sub(r"\n", " ", sanitized_page)
    sanitized_pages.append(sanitized_page)

print(sanitized_pages)
exit(0)

words = []
for page in pages:
    for word in page:

        word = re.sub(r"[w]", "", word)
        word = re.sub(r"_", "", word)
        #words.append(word)
        stuff = re.split(r"\n / ", word)

        words += stuff

print(words)
