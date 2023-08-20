from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup

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

def scrape_jiomart_search():
    # Path to the ChromeDriver executable
    webdriver_path = 'C:\Program Files\chromedriver_win32'
    search_query = input("Enter the search query: ")
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
        if counter >=5:
            break
        driver.get(url)
        time.sleep(2)

        #Titles
        name_element = driver.find_element(By.ID, "pdp_product_name")
        name = name_element.text

        #Prices
        price_element = driver.find_elements(By.ID, 'price_section')
        for price in price_element:
            price_text = price.text.split(" ")[0].split("\n")[0].removesuffix('.00')
            integer_prices = []
            if price_text == ['']:
                integer_prices.append('N/A')
            else:
                integer_prices.append(price_text)
        actual_price = integer_prices[0]
        # print(actual_price)
        
        #Cut Prices
        cut_price_element= driver.find_element(By.ID, 'price_section')
        cut_prices = cut_price_element.find_elements(By.XPATH, '//*[@id="price_section"]/div[2]')
        integer_cut_prices = []
        if cut_prices== []:
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

        #Image_Url
        product_page = requests.get(url)
        soup = BeautifulSoup(product_page.content, 'html.parser')
        img_upper_div = soup.find('div', attrs={'class':'product-image-carousel'})
        img_inner_div = img_upper_div.find('div', attrs={'class':'swiper-wrapper swiper-thumb-wrapper'})
        img_url = img_inner_div.find('img', attrs={'class':'swiper-thumb-slides-img lazyload'}).get('data-src')

        #Ratings
        ratings_section = driver.find_element(By.CLASS_NAME, 'product-rating')
        ratings_div = ratings_section.find_element(By.CLASS_NAME, 'jm-heading-s')
        ratings = ratings_div.text

        
        # BANK_OFFERS
        offers = driver.find_elements(By.XPATH, '//*[@id="offers_popup_content"]//div[@class="product-offer-panel-item jm-ph-m jm-pv-m bank_offers"]//div[@class="jm-list-content-caption-title jm-body-xs-bold"]')
        bank_offers_list = []
        if offers:
            for offer in offers:
                offers_text = offer.get_attribute('innerHTML')
                bank_offers_list.append(offers_text.strip())
                
        #Appending all the scraped details in result list in a dictionary format
        results_list.append({'platform': "Jiomart", "title": name, "price":actual_price, "cut_price":actual_cut_price, 'href':url, "img_url":img_url, "rating":ratings, "offers":bank_offers_list})

        results = [data for data in results_list if data.get('price')!='N/A']

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
        counter +=1

    print(results)

    # Close the browser
    driver.quit()
scrape_jiomart_search()
