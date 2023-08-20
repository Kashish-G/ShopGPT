import requests
import re
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://www.croma.com/televisions-accessories/c/997"

response = requests.get(base_url)
response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

script_tag = soup.find_all("script", {"type": "application/ld+json"})

if len(script_tag) >= 3:
    third_script = script_tag[2]
    script_code = third_script.string

    # Find "itemListElement" array within script code
    start_index = script_code.find('"itemListElement": [')
    end_index = script_code.find(']', start_index) + 1
    item_list_element = script_code[start_index:end_index]

    # Parse the "itemListElement" JSON array
    items = json.loads('{' + item_list_element + '}')['itemListElement']

    for item in items:
        name = item['item']['name']
        url = item['item']['url']
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        script_tag = soup.find("script", {"type": "application/ld+json"})
        script_code = script_tag.string
        
        # Extract the price using regular expressions
        price_match = re.search(r'"price":\s*"([^"]+)"', script_code)
        price = price_match.group(1) if price_match else "N/A"
        rating = soup.find("div",{"class":"cp-rating"})
        rating_score = rating.find("span",{"class":"text"})
        r=rating_score.text
        print("Name:", name)
        print("URL:", url)
        print("Price:", price)
        print(r)
        offers = soup.find_all("div",{"class":"pd-tag"})
        for offer in offers:
            print("Offer:", offer.text.strip())


        
        
        

        print("-" * 40)
else:
    print("Not enough script tags found.")
