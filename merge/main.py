from flask import Flask, jsonify, request
import concurrent.futures
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_cors import CORS
from flask_socketio import SocketIO
import concurrent.futures
import threading
import json
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, origins='*')

def scrape_combined_search(query):
    # Define include keywords
    include_keywords = ["from", "only", "only from","from only","include","including","in"]
    exclude_keywords = ["not from", "except", "exclude","excludes","excluding","not in"]  # Add more keywords as needed

    # Check if any include keyword is present in the query
    include_index = -1
    exclude_index = -1

    for keyword in exclude_keywords:
        keyword_index = query.lower().find(keyword)
        if keyword_index != -1:
            exclude_index = keyword_index
            break
    for keyword in include_keywords:
        keyword_index = query.lower().find(keyword)
        if keyword_index != -1:
            include_index = keyword_index
            break
    websites = [] 
    
    if exclude_index != -1:
        # Extract the product request and excluded websites
        product_request = extract_product_request(query[:exclude_index].strip())
        excluded_websites = [website.strip() for website in query[exclude_index + len(exclude_keywords[0]):].split(",")]

        # Scrape for all websites except excluded websites
        all_websites = [
            "flipkart",
            "amazon",
            "shopclues",
            "jiomart",
            "reliance digital",
            "indiamart",
            "snapdeal",
            "aditya vision",
            "vijay sales"
        ]
        websites = [website for website in all_websites if website not in excluded_websites]

    elif include_index != -1:
        # Extract the product request and websites
        product_request = extract_product_request(query[:include_index].strip())
        websites = [website.strip() for website in query[include_index + len(include_keywords[0]):].split(",")]
    else:
        # Consider the entire query as the product request
        product_request = extract_product_request(query.strip())

        # Scrape for all websites
        websites = [
            "Flipkart",
            "Amazon",
            "Shopclues",
            "JioMart",
            "Reliance Digital",
            "IndiaMart",
            "SnapDeal",
            "Aditya Vision",
            "Vijay Sales"
        ]

    # Store extracted websites in a list
    extracted_websites = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of functions to scrape each website
        scraping_functions = [
            (scrape_flipkart_search, "flipkart"),
            (scrape_amazon_search, "amazon"),
            (scrape_shopclues_search, "shopclues"),
            (scrape_jiomart_search, "jiomart"),
            (scrape_reliance_digital_search, "reliance digital"),
            (scrape_indiamart_search, "indiamart"),
            (scrape_snapdeal_search, "snapdeal"),
            (scrape_adityavision_search, "aditya vision"),
            (scrape_vijaysales_search, "vijay sales")
        ]

        # Print the found website names
        print("Found Website Names:")
        for website in websites:
            if website.strip().lower() in query.lower():
                extracted_websites.extend([w.strip().lower() for w in website.split('and')])
                print(website.strip().lower())

        # If no extracted websites, scrape for all websites
        if not extracted_websites:
            extracted_websites = [website[1] for website in scraping_functions]
            filtered_scraping_functions = [(f, website) for f, website in scraping_functions if website in extracted_websites]

        # Filter scraping functions based on the extracted websites
        if exclude_index!=-1:
            filtered_scraping_functions = [(f, website) for f, website in scraping_functions if website not in extracted_websites]
        if include_index!=-1:
            filtered_scraping_functions = [(f, website) for f, website in scraping_functions if website in extracted_websites]

        results = []
        # for f, website in filtered_scraping_functions:
        def scrape_site(scraping_function, website):
            try:
                result = scraping_function(product_request)
                # result = f(product_request)
                if result:
                    # Create the response dictionary
                    response = {
                        "status": "success",
                        "code": 200,
                        "data": result
                    }
             
                    socketio.emit('scraped_data', response)
                    # results.append(result)
                    
                else:
                    print(f"No data found for {website}.")
            except Exception as e:
                error_response = {
                    "status": "error",
                    "code": 500,
                    "message": "Scraping encountered an error."
                }
                socketio.emit('scraped_data', error_response)
                print(f"Error while scraping {website}: {str(e)}")

        threads = []
        for f, website in filtered_scraping_functions:
            thread = threading.Thread(target=scrape_site, args=(f, website))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish:
        for thread in threads:
            thread.join()

        # Return a success response
        response_ = {'status': 'success', 'message': 'Scraping completed'}
        return response_
        # # Combine the results
        # combined_results = []
        # for result in results:
        #     combined_results.extend(result)
        # response = {'status': 'success', 'data': combined_results}
        # return response
def extract_product_request(query):
    product_request = ""

    # Split the query into individual words
    words = query.lower().split()

    # Define a set of keywords for product requests
    product_keywords = ["a", "an", "buy", "purchase", "get", "find", "want", "looking", "for", "show", "display"]

    # Find the relevant keywords and extract the product request
    keyword_indices = [index for index, word in enumerate(words) if word in product_keywords]
    if keyword_indices:
        last_keyword_index = keyword_indices[-1]
        product_request = " ".join(words[last_keyword_index + 1:])
    else:
        product_request = query.strip()

    return product_request
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

def scrape_flipkart_search(query):
    base_url = "https://www.flipkart.com/search"
    params = {"q": query}

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    search_results = soup.find_all("div", {"class": "_1AtVbE"})

    counter = 0  # Counter to keep track of non-advertisement products
    results = []

    for result in search_results:
        if counter >= 5:
            break  # Stop iterating once 5 non-advertisement products are found

        if result.find("div", class_=["_1xHGtK _373qXS", "_4ddWXP"]):
            inner_products = result.find_all("div", class_=["_1xHGtK _373qXS", "_4ddWXP"])

            for inner_product in inner_products:
                ad_flag_inner = inner_product.find("div", class_=["_2I5qvP", "_4HTuuX"])

                if not ad_flag_inner:  # Check if the inner product is an advertisement
                    title_element_inner = inner_product.find("a", class_=["IRpwTa", "s1Q9rs"])
                    if not title_element_inner:
                        continue

                    title_inner = title_element_inner.text.strip()

                    price_element_inner = inner_product.find("div", {"class": "_30jeq3"})
                    if not price_element_inner:
                        continue
                    
                    price_list = []
                    price_inner = price_element_inner.text.strip()
                    price_list.append(price)

                    href_element_inner = inner_product.find("a", class_=["_2UzuFa", "s1Q9rs"])
                    if not href_element_inner:
                        continue

                    href_inner = urljoin("https://www.flipkart.com", href_element_inner["href"])

                    img_div_inner = inner_product.find('div', attrs={'class': 'CXW8mj'})
                    img_tag_inner = img_div_inner.find('img', attrs={'class': '_396cs4'})
                    if not img_tag_inner:
                        continue

                    img_url_inner = img_tag_inner.get('src')

                    rating_element_inner = inner_product.find("div", class_=["_3LWZlK _1rdVr6 _1BLPMq", "_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq", "_3LWZlK"])
                    if rating_element_inner:
                        rating_inner = rating_element_inner.text.strip()
                    else:
                        continue

                    results.append({
                        "platform": "Flipkart",
                        "title": title_inner,
                        "price": price_inner,
                        "href": href_inner,
                        "img_url": img_url_inner,
                        "rating": rating_inner
                    })

                    counter += 1

                    # Fetching offers from the URL
                    response_inner = requests.get(href_inner)
                    soup_inner = BeautifulSoup(response_inner.content, "html.parser")
                    offers = soup_inner.find_all("li", {"class": "_16eBzU col"})
                    for offer in offers:
                        results[-1].setdefault("offers", []).append(offer.text.strip())
                    reviews = soup_inner.find("span", {"class": "_2_R_DZ"})
                    if reviews:
                        reviews_text = reviews.text.strip()
                        reviews_number = reviews_text.split("&")[-1].strip()
                        results[-1]["reviews"] = reviews_number
                    cut_price_element = soup_inner.find("div", {"class": "_3I9_wc _2p6lqe"})
                    if cut_price_element:
                        cut_price = cut_price_element.text.strip()
                        results[-1]["cut_price"] = cut_price

                    #coupons
                    coupon_price_list = []
                    for prices in price_list:
                        without_special_symbol = prices.removeprefix("₹").replace(",", "")
                        price_int = int(without_special_symbol)
                        coupon_price_float = price_int * 0.05
                        coupon_price_list.append(str(round(coupon_price_float)))

                    coupon_price_singal_digit = []
                    for i in coupon_price_list:
                        for char in i:
                            coupon_price_singal_digit.append(char)
                    print(coupon_price_singal_digit)
                    coupon_price_val = coupon_price(coupon_price_singal_digit)
                    
                    results[-1]['after 5%'] = coupon_price_list
                    results[-1]['coupon_val'] = coupon_price_val

        else:
            ad_flag = result.find("div", {"class": "_2tfzpE"})

            if not ad_flag:  # Check if the result is an advertisement
                title_element = result.find("div", {"class": "_4rR01T"})
                if not title_element:
                    continue

                title = title_element.text.strip()

                price_element = result.find("div", {"class": "_30jeq3"})
                if not price_element:
                    continue
                
                price_list = []
                price = price_element.text.strip()
                price_list.append(price)

                href_element = result.find("a", {"class": "_1fQZEK"})
                if not href_element:
                    continue

                href = urljoin("https://www.flipkart.com", href_element["href"])

                img_div = result.find('div', attrs={'class': 'CXW8mj'})
                img_tag = img_div.find('img', attrs={'class': '_396cs4'})
                if not img_tag:
                    continue

                img_url = img_tag.get('src')

                rating_element = result.find("div", class_=["_3LWZlK _1rdVr6 _1BLPMq", "_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq", "_3LWZlK"])
                if rating_element:
                    rating = rating_element.text.strip()
                else:
                    continue

                results.append({
                    "platform": "Flipkart",
                    "title": title,
                    "price": price,
                    "href": href,
                    "img_url": img_url,
                    "rating": rating
                })

                counter += 1

                # Fetching offers from the URL
                response_inner = requests.get(href)
                soup_inner = BeautifulSoup(response_inner.content, "html.parser")
                offers = soup_inner.find_all("li", {"class": "_16eBzU col"})
                for offer in offers:
                    results[-1].setdefault("offers", []).append(offer.text.strip())
                reviews = soup_inner.find("span", {"class": "_2_R_DZ"})
                if reviews:
                    reviews_text = reviews.text.strip()
                    reviews_number = reviews_text.split("&")[-1].strip()
                    results[-1]["reviews"] = reviews_number
                cut_price_element = soup_inner.find("div", {"class": "_3I9_wc _2p6lqe"})
                if cut_price_element:
                    cut_price = cut_price_element.text.strip()
                    results[-1]["cut_price"] = cut_price

                #coupons
                    coupon_price_list = []
                    for prices in price_list:
                        without_special_symbol = prices.removeprefix("₹").replace(",", "")
                        price_int = int(without_special_symbol)
                        coupon_price_float = price_int * 0.05
                        coupon_price_list.append(str(round(coupon_price_float)))

                    coupon_price_singal_digit = []
                    for i in coupon_price_list:
                        for char in i:
                            coupon_price_singal_digit.append(char)
                    coupon_price_val = coupon_price(coupon_price_singal_digit)
                    
                    results[-1]['after 5%'] = coupon_price_list
                    results[-1]['coupon_val'] = coupon_price_val

    return results

def scrape_shopclues_search(query):
    base_url = "https://www.shopclues.com/search"
    params = {"q": query}

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    search_results = soup.find_all("div", {"class": "column col3 search_blocks"})
    
    counter = 0  # Counter to keep track of non-advertisement products
    results =[]
    for search_result in search_results:
        if counter >= 5:
            break  # Stop iterating once 5 non-advertisement products are found

        title_element = search_result.find("h2")
        title = title_element.text
        result = {"id":counter, "platform":"Shopclues", 'title':title}

        price_list = []
        price_element = search_result.find("span", {"class": ["p_price", "f_price"]})
        price = price_element.text.strip()
        result['price'] = price
        price_list.append(price)
       
        href_element = search_result.find("a")
        href = urljoin("https://www.shopcules.com", href_element["href"])
        result['href'] = href
       
        #Image Urls
        img_div = search_result.find('div', attrs={'class':'img_section'})
        img_tag = img_div.find('img')
        img_url = img_tag.get('data-img')
        result['img_url'] = img_url
        
        #Bank offers
        response_inner = requests.get(href)
        soup_inner = BeautifulSoup(response_inner.content, "html.parser")
        offers = soup_inner.find_all("li", {"class": "pdp_offrs"})
        offers_list = []
        if offers is not None:
            for offer in offers:
                offer_text = " ".join(offer.text.split())
                offers_list.append(offer_text)
                result['offers'] = offers_list
        else:
            result['offers'] = []

        #Cut Price
        cut_price_element = soup_inner.find('span', attrs={'id':'sec_list_price_'})
        if cut_price_element is not None:
            cut_price = cut_price_element.text.split(":")[1]
            result['cut_price'] = cut_price
        else:
            result['cut_price'] = "N/A"
        
        #Rating
        rating_element = soup_inner.find('div', attrs={'class', "star_rating_point"})
        if rating_element is not None:
            rating = rating_element.text.strip()
            if rating == '0':
                result['rating'] = ""
            else:
                result['rating'] = rating
        else:
            result['rating'] = ""
        
        #Reviwes
        reviews_element = soup_inner.find('div', attrs={'class':'rnr_bar'})
        if reviews_element is not None:
            reviews_text = reviews_element.find('p')
            reviews = reviews_text.text.split(",")[1].removesuffix("Reviews").strip()
            if reviews == '0':
                result['reviews'] = ""
            else:
                result['reviews'] = reviews
        else:
            result['reviews'] = ""

        #coupons
        coupon_price_list = []
        for prices in price_list:
            without_special_symbol = prices.removeprefix("₹").replace(",", "")
            price_int = int(without_special_symbol)
            coupon_price_float = price_int * 0.03
            coupon_price_list.append(str(round(coupon_price_float)))

        coupon_price_singal_digit = []
        for i in coupon_price_list:
            for char in i:
                coupon_price_singal_digit.append(char)

        coupon_price_val = coupon_price(coupon_price_singal_digit)
        result['coupon_val'] = coupon_price_val

        results.append(result)
        counter += 1

    return results

def scrape_adityavision_search(search_query):
    results = []
    # search_query = input("Enter the search query: ")
    base_url = "https://adityavision.com/catalogsearch/result/?cat=&ip_address=49.248.155.62&q="+search_query

    response = requests.get(base_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    search_results = soup.find_all("li", {"class": "item product product-item"})

    counter = 0  # Counter to keep track of non-advertisement products

    for detail in search_results:
        if counter >= 5:
            break  # Stop iterating once 5 non-advertisement products are found

        title_element = detail.find("a", {"class": "product-item-link"})
        if title_element:
            title = title_element.text.strip()  # Remove leading and trailing whitespace
            result = {'title':title}
        else:
            continue

        price_element = detail.find("span", {"class": "special-price"})
        if price_element:
            # Remove leading and trailing whitespace
            price = price_element.text.replace('From',"").strip().removesuffix('.00')
            result['price']=price
        else:
            continue

        href_element = detail.find("a", {"class": "product-item-link"})
        if href_element:
            href = href_element["href"]
            result['href']=href
        else:
            continue
        
        #IMAGE_URLs
        img_element_span = detail.find('span', attrs={'class':'product-image-wrapper'})
        img_tag = img_element_span.find_all('img', attrs={'class':'product-image-photo'})
        for img in img_tag:
            img_url = img.get('src')
            result['img_url']=img_url

        #Cut_prices
        cut_price_element_one = detail.find('span', attrs={'class':'old-price'})
        cut_price_element_two = cut_price_element_one.find('span', attrs={'class':'price'})

        if cut_price_element_two is None:
            result['cut_price'] = 'Not defined'
        else:
            cut_price = cut_price_element_two.text.strip().removesuffix('.00')
            result['cut_price']=cut_price

        result["platform"] = "Aditya Vision"
        results.append(result)
        counter += 1
        
    return results        

def scrape_jiomart_search(search_query):
    # Path to the ChromeDriver executable
    webdriver_path = 'C:\Program Files\chromedriver_win32'
    # search_query = input("Enter the search query: ")
    # Set the URL of the JioMart page you want to scrape
    url = "https://www.jiomart.com/search/"+search_query

    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without opening the browser window)

    # Start the Selenium WebDriver
    driver = webdriver.Chrome(service=Service(executable_path=webdriver_path), options=chrome_options)

    # Navigate to the URL
    driver.get(url)

    # Wait for the page to fully render (you can adjust the sleep time as needed)
    time.sleep(2)

    results_list = []
    # Find the relevant elements using Selenium's find_elements method
    product_items = driver.find_elements(By.CLASS_NAME, "jm-col-4.jm-mt-base")

    urls_list = []
    for item in product_items:
        link_element = item.find_elements(By.TAG_NAME, "a")
        for url in link_element:
            href_inner = url.get_attribute("href")
            urls_list.append(href_inner)

    counter = 0
    for url in urls_list:
        if counter >= 5:
            break
        driver.get(url)
        time.sleep(2)

        # Titles
        name_element = driver.find_element(By.ID, "pdp_product_name")
        name = name_element.text

        # Prices
        price_element = driver.find_elements(By.ID, 'price_section')
        for price in price_element:
            price_text = price.text.split(" ")[0].split("\n")[0].removesuffix('.00')
            integer_prices = []
            if price_text == ['']:
                integer_prices.append('N/A')
            else:
                integer_prices.append(price_text)
        actual_price = integer_prices[0]

        # Cut Prices
        cut_price_element = driver.find_element(By.ID, 'price_section')
        cut_prices = cut_price_element.find_elements(By.XPATH, '//*[@id="price_section"]/div[2]')
        integer_cut_prices = []
        if cut_prices == []:
            integer_cut_prices.append('N/A')
        else:
            for cut_price in cut_prices:
                cut_price_text = cut_price.text.split(" ")[1].split("\n")
                if cut_price_text == ['']:
                    integer_cut_prices.append('N/A')
                else:
                    for i in cut_price_text:
                        for chr in i:
                            if chr.isdigit():
                                integer_cut_prices.append(i)
        cut_price = list(dict.fromkeys(integer_cut_prices))
        actual_cut_price = cut_price[0]

        # Image_Url
        product_page = requests.get(url)
        soup = BeautifulSoup(product_page.content, 'html.parser')
        img_upper_div = soup.find('div', attrs={'class': 'product-image-carousel'})
        img_inner_div = img_upper_div.find('div', attrs={'class': 'swiper-wrapper swiper-thumb-wrapper'})
        img_url = img_inner_div.find('img', attrs={'class': 'swiper-thumb-slides-img lazyload'}).get('data-src')

        # Ratings
        ratings_section = driver.find_element(By.CLASS_NAME, 'product-rating')
        ratings_div = ratings_section.find_element(By.CLASS_NAME, 'jm-heading-s')
        ratings = ratings_div.text

        # BANK_OFFERS
        offers = driver.find_elements(By.XPATH,
                                      '//*[@id="offers_popup_content"]//div[@class="product-offer-panel-item jm-ph-m jm-pv-m bank_offers"]//div[@class="jm-list-content-caption-title jm-body-xs-bold"]')
        bank_offers_list = []
        if offers:
            for offer in offers:
                offers_text = offer.get_attribute('innerHTML')
                bank_offers_list.append(offers_text.strip())

        # Appending all the scraped details in result list in a dictionary format
        results_list.append(
            {'platform': "Jiomart", "title": name, "price": actual_price, "cut_price": actual_cut_price,
             'href': url, "img_url": img_url, "rating": ratings, "offers": bank_offers_list})

        results = [data for data in results_list if data.get('price') != 'N/A']

        #coupons
        for result in results:
            if 'price' in result:
                coupon_price_list =[]
                prices = result['price']
                without_special_symbol = prices.removeprefix("₹").replace(",","")
                price_int = int(without_special_symbol)
                coupon_price_float = price_int * 0.04
                coupon_price_list.append(str(round(coupon_price_float)))
            
                coupon_price_singal_digit = []
                for i in coupon_price_list:
                    for char in i:
                        coupon_price_singal_digit.append(char)
                coupon_price_val = coupon_price(coupon_price_singal_digit)

                result['coupon_val'] = coupon_price_val

        counter += 1
    return results[:5]  # Return only the first 5 results


def scrape_indiamart_search(query):
    url = "https://dir.indiamart.com/search.mp?ss=" + query

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
            

            # Check if the product details are not empty and not already printed
            if title and price and href and img_url and (title, price, href, img_url) not in product_set:
                results.append({"platform": "IndiaMART", "title": title, "price": price, "href": href, 'img_url':img_url})

                # Add the product details to the set
                product_set.add((title, price, href, img_url))

                # Increment the counter
                counter += 1

                # Break the loop if 5 products have been found
                if counter == 5:
                    break

        # Break the loop if 5 products have been found
        if counter == 5:
            break

    return results

def scrape_snapdeal_search(query):
    base_url = f"https://www.snapdeal.com/search?keyword={query}"
    time.sleep(2)
    useragent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    web_page = requests.get(base_url, headers=useragent)
    web_page.raise_for_status

    soup = BeautifulSoup(web_page.content, 'html.parser')

    # PRODUCT_LINK
    main_div = soup.find('div', attrs={
                        'class': 'comp comp-right-wrapper ref-freeze-reference-point clear'})
    # URLS
    product_url = main_div.find_all(
        'div', attrs={'class': 'product-desc-rating'})

    counter = 0
    results = []
    for url in product_url:
        if counter >= 5:
            break
        # URLS
        find_link = url.find('a')
        link = find_link.get('href')
        result = {"platform":"Snapdeal", 'href':link}

        new_webpage = requests.get(link, headers=useragent)
        new_webpage.raise_for_status()
        new_soup = BeautifulSoup(new_webpage.content, 'html.parser')

        # TITLES
        title_element = new_soup.find_all('h1', attrs={'class': 'pdp-e-i-head'})
        for i in title_element:
            title_text = i.get_text()
            title = title_text.strip()
            result['title'] = title

        # PRICES
        price_element = new_soup.find(
            'div', attrs={'class': "pdp-e-i-PAY-r disp-table-cell lfloat"})
        price_txt = price_element.find_all('span', attrs={'class': "payBlkBig"})
        for i in price_txt:
            price = i.get_text()
            result['price'] = '₹' + price

        # BANK OFFERS
        offers_div_one = new_soup.find_all('div', attrs={'class': "offerBlock clearfix"})
        offers_list = []

        if offers_div_one is not None:
            for i in offers_div_one:
                offers_text = i.get_text()
                offer_pure_text = offers_text.strip().replace('T&C', "")
                offers = offer_pure_text.strip()
                offers_list.append(offers)
        else:
            offers_list = []

        result['offers'] = offers_list


        # IMAGE_URLs
        img_ul_tag = new_soup.find(
            'ul', attrs={'id': 'bx-slider-left-image-panel'})
        img_tag = img_ul_tag.find('img').get('bigsrc')
        img_url = img_tag
        result['img_url'] =img_url

        #cut_price
        cut_price_element = new_soup.find('div', attrs={'class':'pdpCutPrice'})
        cut_price = cut_price_element.text.split(" ")[0].removesuffix("(Inclusive").strip().removeprefix('MRP').strip().removeprefix('Rs.').strip()
        result['cut_price'] = '₹' +  cut_price

        #rating
        rating_element = new_soup.find('div', attrs={'class':'pdp-e-i-ratings'})
        if rating_element is not None:
            rating_text = rating_element.find('span', attrs={'class':'avrg-rating'})
            rating = rating_text.text.replace("(", "").replace(")","").strip()
            result['rating'] = rating
        else:
            result['rating'] = ""

        #reviwes
        reviwes_element = new_soup.find('span', attrs={'class':'numbr-review'})
        if reviwes_element is not None:
            reviews = reviwes_element.text.split(" ")[0].strip()
            result['reviews']=reviews
        else:
            result['reviews'] = ""
        results.append(result)
        counter += 1

    return results

def scrape_reliance_digital_search(query):
    base_url = f"https://www.reliancedigital.in/search?q={query}"
    time.sleep(1)
    useragent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    web_page = requests.get(base_url, headers=useragent)
    web_page.raise_for_status()
    soup = BeautifulSoup(web_page.content, 'html.parser')

    product_url_div = soup.find('div', attrs={'class':"pl__container"})
    half_url =  product_url_div.find_all("a", attrs={'attr-tag':'anchor'})

    results = []
    counter = 0

    for url in half_url:
        if counter >= 5:
            break

        # URLs
        complete_url = "https://www.reliancedigital.in" + url.get("href")
        result = {"href": complete_url}

        new_webpage = requests.get(complete_url, headers=useragent)
        new_webpage.raise_for_status()
        new_soup = BeautifulSoup(new_webpage.content, 'html.parser')

        # Titles
        titles = new_soup.find_all('h1', attrs={"class":"pdp__title"})
        for title in titles:
            title_pure_txt = title.get_text()
            result["title"] = title_pure_txt

        # Prices
        prices_div = new_soup.find("li", attrs={'class':'pdp__priceSection__priceListText'})
        prices_txt = prices_div.find_all('span', attrs={'class' :['TextWeb__Text-sc-1cyx778-0 cJQfDP', 'TextWeb__Text-sc-1cyx778-0 kFBgPo']})

        price_list = []
        for price in prices_txt:
            prices = price.get_text()
            price_without_decimal = prices.split(".")[0]
            result["price"] = price_without_decimal
            price_list.append(price_without_decimal)

        #Cut_price
        cut_price_element = new_soup.find('span', attrs={'class':['TextWeb__Text-sc-1cyx778-0 ckoPIR', 'TextWeb__Text-sc-1cyx778-0 bNdnUu']})
        if cut_price_element is not None:
            cut_price = cut_price_element.text
            cut_price_without_decimal = cut_price.split(".")[0]
            result['cut_price'] = cut_price_without_decimal
        else:
            result['cut_price'] = 'N/A'

        #Image Urls
        image_div = new_soup.find('div', attrs={'class':'pdp__imgZoomContainer'})
        img_tag = image_div.find_all('img', attrs={'id':'myimage'})
        for img in img_tag:
            img_half_url = img.get('data-srcset')
            complete_img_url = 'https://www.reliancedigital.in' + img_half_url
            result['img_url'] = complete_img_url
           
        #Ratings
        rating_div_one =  new_soup.find('div', attrs={'id':'reviews'})
        rating_txt = rating_div_one.find('span', attrs={'class':'TextWeb__Text-sc-1cyx778-0 emga-Df Block-sc-u1lygz-0 iJOtqd'})
        if rating_txt is not None:
            rating_pure_txt = rating_txt.getText()
            result['rating'] = rating_pure_txt
        else:
            result['rating'] = ""
            
        #Reviews
        reviews_div = new_soup.find('div', attrs={'id':"reviews"})
        reviews_text = reviews_div.find_all('span', attrs={'class':'TextWeb__Text-sc-1cyx778-0 gEyFve Block-sc-u1lygz-0 SpmXl'}) 
        if reviews_text == [] or reviews_text == "":
            result['reviews'] = ""
        else:
            for review in reviews_text:
                review_pure_text = review.get_text()
                result['reviews'] = review_pure_text

        # Bank Offers
        offers_li = new_soup.find('ul', attrs={'class':"pdp__ulListMain"})
        if offers_li is not None:
            offers_txt = offers_li.find_all('span')
            offers = [offer.get_text().replace("Read-T&C", "").replace('See More', "").replace("TnC Apply*", "").strip() for offer in offers_txt]
            result["offers"] = offers
        else:
            result["offers"] = ""
        
        #coupons
        coupon_price_list = []
        for prices in price_list:
            without_special_symbol = prices.removeprefix("₹").replace(",", "")
            price_int = int(without_special_symbol)
            coupon_price_float = price_int * 0.022
            coupon_price_list.append(str(round(coupon_price_float)))

        coupon_price_singal_digit = []
        for i in coupon_price_list:
            for char in i:
                coupon_price_singal_digit.append(char)
        coupon_price_val = coupon_price(coupon_price_singal_digit)
        result['coupon_val'] = coupon_price_val
            
        result["platform"] = "Reliance Digital"
        results.append(result)

        counter += 1

    return results

def scrape_amazon_search(query):
    page = 1
    results = []
    counter = 0

    while page != 2 and counter <= 6:
        base_url = f'https://www.amazon.in/s?k={query}&page={page}'
        user_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

        web_page = requests.get(base_url, headers=user_agent)
        web_page.raise_for_status()
        soup = BeautifulSoup(web_page.content, 'html.parser')

        product_urls = soup.find_all('a', attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})

        if product_urls is None:
            print('Product URLs Not Found!')
        else:
            for url in product_urls:
                #url
                link = 'https://www.amazon.in' + url.get('href')

                new_webpage = requests.get(link, headers=user_agent)
                new_soup = BeautifulSoup(new_webpage.content, 'html.parser')

                product_names = new_soup.find_all('span', attrs={'id': 'productTitle'})
                for name in product_names:
                    name_txt = name.get_text()
                    title = name_txt.strip()

                #price
                price_text = new_soup.find('span', attrs={'class':'a-price-whole'}).text
                price = "₹"+price_text

                # prices = new_soup.find_all('span', attrs={'class': 'a-price-whole'})
                # for price in prices:
                #     price = price.get_text()

                #CUT_PRICES
                cut_prices_div = new_soup.find('div', attrs={'class':'a-section a-spacing-small aok-align-center'})
                if cut_prices_div is not None:
                    cut_price = cut_prices_div.find('span', attrs={'class':'a-offscreen'}).text
                else:
                    cut_price = 'N/A'

                #asin
                splitting_asin = link.split('dp')
                a = splitting_asin[1]
                slicing = a[1:13:1]
                modifying1 = slicing.removeprefix("2F")
                asin = modifying1.removesuffix('/r')

                #Ratings
                ratings_txt = new_soup.find('div', attrs={'id':'averageCustomerReviews'})
                if ratings_txt is not None:
                    rating = ratings_txt.find('span', attrs={'class':'a-size-base a-color-base'}).text.strip()
                else:
                    rating = "No rating"

                #Reviews
                reviews_element = new_soup.find('a', attrs={'id':'askATFLink'})
                if reviews_element is not None:
                    reviews = new_soup.find('a', attrs={'id':'askATFLink'}).text.strip().split(" ")[0]
                else:
                    reviews = 'No reviews'
                
                #img_urls
                img_div = new_soup.find('div', attrs={'class':'imgTagWrapper'})
                img_tag = img_div.find_all('img', attrs={'id': 'landingImage'})
                for img in img_tag:
                    img_url = img.get('src')
                
                result = {
                        'platform': "Amazon",
                        'href': link,
                        'title': title,
                        'img_url':img_url,
                        'price': price,
                        'cut_price':cut_price,
                        'rating' : rating,
                        'reviwes' : reviews,
                        'offers': []
                    }

                #coupons
                coupon_price_list = []
                actual_price  = result['price'].replace(",", "").removeprefix('₹').removesuffix('.')
                price_int = int(actual_price)
                coupon_price_float = price_int * 0.025
                coupon_price_list.append(str(round(coupon_price_float)))
                
                coupon_price_singal_digit = []
                for i in coupon_price_list:
                    for char in i:
                        coupon_price_singal_digit.append(char)
                coupon_price_val = coupon_price(coupon_price_singal_digit)
                result['coupon_val'] = coupon_price_val

                #bank offers
                bank_offer_num = new_soup.find('div', attrs={'id': 'itembox-InstantBankDiscount'})
                if bank_offer_num is not None:
                    bank_offer_num_txt = bank_offer_num.find('a', attrs={'class': 'a-size-base a-link-emphasis vsx-offers-count'}).string.strip().split(" ")[1]
                else:
                    bank_offer_num_txt = ""

                bank_offer_url = f"https://www.amazon.in/hctp/vsxoffer?asin={asin}&deviceType=web&offerType=InstantBankDiscount&buyingOptionIndex"
                time.sleep(2)
                try:
                    request_bank_offer = requests.get(bank_offer_url, headers=user_agent)
                    request_bank_offer.raise_for_status()
                    soup_bank_offer = BeautifulSoup(request_bank_offer.content, 'html.parser')
                    
                    if bank_offer_num_txt == 'offers':
                        bank_offers = soup_bank_offer.find_all('p', attrs={'class': 'a-spacing-mini a-size-base-plus'})
                        result["offers"] = [offer.get_text() for offer in bank_offers]
                    else:
                        bank_offer = soup_bank_offer.find_all('h1', attrs={'class': 'a-size-medium-plus a-spacing-medium a-spacing-top-small'})
                        result["offers"] = [offer.get_text().strip() for offer in bank_offer]

                    results.append(result)

                    counter += 1
                    if counter >= 5:
                        break

                except requests.exceptions.HTTPError as e:
                    print(f"Error fetching bank offers for URL: {bank_offer_url}")
                    print(f"Exception: {str(e)}")
                
        page += 1
        print(results)

    return results


def scrape_vijaysales_search(query):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    base_url = f"https://www.vijaysales.com/search/{query}"
    driver.get(base_url)

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[4]/div[9]/div/div[2]/div[2]/div[2]/div[2]/div[3]')))
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='col-lg-12 col-xs-12']")))

    single_product_div = driver.find_elements(By.XPATH, "//*[@id='ContentPlaceHolder1_DivResultContainer']//div[@class='col-lg-12 col-xs-12']")

    href = driver.find_elements(By.XPATH, "//*[@id='ContentPlaceHolder1_DivResultContainer']//a[@class='nabprod']")
    counter = 1
    results = []

    if single_product_div == []:
        while True:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='ContentPlaceHolder1_DivResultContainer']//div[@class='col-lg-12 col-xs-12']")))
            time.sleep(2)
    else:
        while counter <= 5:
            for i in href:
                urls = i.get_attribute('href')
                # URLs
                result = {"platform": "Vijay Sales", 'href': urls}

                # Passing a request to product urls
                web_page = requests.get(urls)
                web_page.raise_for_status()
                soup = BeautifulSoup(web_page.content, 'html.parser')

                # IMAGE_URLs
                img = soup.find('img', attrs={'id': 'ContentPlaceHolder1_ProductImage'}).get('src')
                result['img_url'] = img

                # TITLES
                titles = soup.find_all('h1', attrs={'id': 'ContentPlaceHolder1_h1ProductTitle'})
                for title in titles:
                    title_text = title.get_text()
                    result['title'] = title_text

                # PRICES
                prices_div = soup.find('div', attrs={'class': 'priceMRP'})
                prices_span = prices_div.find_all('span')
                prices_list = []
                for i in prices_span:
                    prices_list.append(i.get_text())
                index_price = prices_list[1]
                result['price'] = index_price

                # Cut_Price
                cut_price_element = soup.find('span', attrs={'class': 'unstikeprize'})
                if cut_price_element is not None:
                    cut_price = cut_price_element.text
                    result['cut_price'] = cut_price
                else:
                    result['cut_price'] = "N/A"

                results.append(result)
                counter += 1
                if counter > 5:
                    break

    return results



def print_results(results):
    for result in results:
        print("Platform:", result["platform"])
        print("Title:", result["title"])
        print("Price:", result["price"])
        print("Href:", result["href"])
        
        if "offers" in result:
            print("Offers:")
            for offer in result["offers"]:
                print("- ", offer)
        
        if 'img_url' in result:
            for img_url in result['img_url']:
                print("Img Url: ", img_url)

        if 'rating' in result:
            for rating in result['rating']:
                print("Rating: ", rating)

        if 'cut_price' in result:
            for cut_price in result['cut_price']:
                print("Cut_price: ", cut_price)

        if 'reviews' in result:
            for reviews in result['reviwes']:
                print("Reviews: ", reviews)

        
        print("-" * 40)


@app.route('/api/search', methods=['POST', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
        # response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        # response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
        # response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    else:
        search_query = request.json.get('query')
        if not search_query:
            return jsonify({'error': 'No search query provided'}), 400
       
        results = scrape_combined_search(search_query)
        socketio.emit('scraped_data', {'results': results})

        # return jsonify({'status':'success', 'results': results})
        return jsonify({'results': results})

    
# if __name__ == '__main__':
#     socketio.run(app, port=3000, debug=True, use_reloader=True)

# if __name__ == '__main__':
#     app.run(debug=True, port='3000')
if __name__ == '__main__':
    # Use gevent-websocket server to run the app
    http_server = WSGIServer(("127.0.0.1", 3000), app)
    print("Running on http://127.0.0.1:3000")
    http_server.serve_forever()