import requests
from bs4 import BeautifulSoup
import json
def coupon_price(coupon_price_singal_digit):
    modified_coupon_list = coupon_price_singal_digit.copy()
    if modified_coupon_list[-1] != '0':
        modified_coupon_list[-1] = '0'

    if modified_coupon_list[-2] in ['6', '7', '8'] :
        modified_coupon_list[-2] = '5'

    if modified_coupon_list[-2] in ['4', '3', '2', '1']:
        modified_coupon_list[-2] = '0'
        
    coupon_price = int("".join(modified_coupon_list))

    if modified_coupon_list[-2] == '9':
        convert_to_int = int("".join(modified_coupon_list))
        ten = convert_to_int + 10
        coupon_price = ten

    return coupon_price

search_query = input("Enter the search query: ")
url = "https://dir.indiamart.com/search.mp?ss=" + search_query

# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
script_tag = soup.find("script", text=lambda text: text and "window.__INITIAL_DATA__" in text)
script_code = script_tag.string

json_data = script_code.split("window.__INITIAL_DATA__ = ")[-1].split("};")[0] + "}"

# Load the JSON data
initial_data = json.loads(json_data)

# Access the "results" array
results_array = initial_data["results"]

# Initialize a counter variable
counter = 0

# Set to store unique product identifiers
product_set = set()

# List to store the results
results = []

# Iterate over each result
for result in results_array:
    # Access the "similarprod" array inside the result
    similarprod_array = result["similarprod"]

    # Print the details of each similar product
    for similarprod in similarprod_array:
        if similarprod.get("title"):
            title = similarprod.get("title")
        else:
            continue
        price_list = []
        if similarprod.get("price"):
            price = similarprod.get("price")
            price_list.append(price)
        else:
            continue
        if similarprod.get("href"):
            href = similarprod.get("href")
        else: 
            continue
        
        #IMAG_URLs
        if similarprod.get('fullZoomImg'):
            img_url = similarprod.get('fullZoomImg')
        else:
            continue   
    
        #coupons
        coupon_price_list = []
        for i in price_list:
            actual_price  = i.replace(",", "").removeprefix('₹')
            price_int = int(actual_price)
            print(price_int)
            coupon_price_float = price_int * 0.05
            print(coupon_price_float)
        coupon_price_list.append(str(round(coupon_price_float)))
        print(coupon_price_list)

        coupon_price_singal_digit = []
        for i in coupon_price_list:
            for char in i:
                coupon_price_singal_digit.append(char)
        coupon_price_val = coupon_price(coupon_price_singal_digit)
        print(coupon_price_val)

        # Check if the product details are not empty and not already printed
        if title and price and href and img_url and coupon_price_val and (title, price, href, img_url, coupon_price_val) not in product_set:
            results.append({"platform": "IndiaMART", "title": title, "price": price, "href": href, 'img_url':img_url, 'coupon_val':coupon_price_val})


            # Add the product details to the set
            product_set.add((title, price, href, img_url, coupon_price_val))

            # Increment the counter
            counter += 1
            # Break the loop if 5 products have been printed
            if counter == 5:
                break

    # Break the loop if 5 products have been printed
    if counter == 5:
        break
print(results)