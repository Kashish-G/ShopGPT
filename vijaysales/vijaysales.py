from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests

def scrape_vijaysales_search():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    
    query = input("Enter a product name: ")
    base_url = f"https://www.vijaysales.com/search/{query}"
    driver.get(base_url)

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[4]/div[9]/div/div[2]/div[2]/div[2]/div[2]/div[3]')))
    wait.until(EC.presence_of_element_located((By.XPATH,"//*[@class='col-lg-12 col-xs-12']")))


    single_product_div =driver.find_elements(By.XPATH,"//*[@id='ContentPlaceHolder1_DivResultContainer']//div[@class='col-lg-12 col-xs-12']")
    # print(single_product_div)

    href = driver.find_elements(By.XPATH, "//*[@id='ContentPlaceHolder1_DivResultContainer']//a[@class='nabprod']")
    counter = 1
    results = []


    if single_product_div==[]:
        while True:
            wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='ContentPlaceHolder1_DivResultContainer']//div[@class='col-lg-12 col-xs-12']")))
            time.sleep(2)
    else:
        while counter <= 5:
            for i in href:
                urls = i.get_attribute('href')
                # driver.get(urls)
                # wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="form1"]/div[4]/div[11]/div/div[4]')))
                time.sleep(5)
                #URLs
                result = {'href':urls}

                #Passing a request to product urls
                web_page = requests.get(urls)
                web_page.raise_for_status()
                soup = BeautifulSoup(web_page.content, 'html.parser')

                #IMAGE_URLs
                img_url = soup.find('img', attrs={'id':'ContentPlaceHolder1_ProductImage'}).get('src')
                result['img_url'] = img_url

                #TITLES
                titles = soup.find_all('h1', attrs={'id':'ContentPlaceHolder1_h1ProductTitle'})
                for title in titles:
                    title_text = title.get_text()      
                    result['title'] = title_text

                #PRICES
                prices_div = soup.find('div', attrs={'class':'priceMRP'})
                prices_span = prices_div.find_all('span')
                prices_list = []
                for i in prices_span:
                    prices_list.append(i.get_text())
                price = prices_list[1]
                result['price'] = price

                #Cut_Price
                cut_price_element = soup.find('span', attrs={'class':'unstikeprize'})
                if cut_price_element is not None:
                    cut_price = cut_price_element.text
                    result['cut_price'] = cut_price
                else:
                    result['cut_price'] = "N/A"
                
                #Rating
                # rating_element = soup.find('div', attrs={'id':'ContentPlaceHolder1_dvRateReview'})
                # if rating_element is not None:
                #     rating = rating_element.find('span', attrs={'class':'starcolor'}).text
                #     result['rating'] = rating
                # else:
                #     result['rating'] = ""
                
                #Reviews
                # reviews_element = soup.find('div', attrs={'id':'ContentPlaceHolder1_dvRateReview'})
                # if reviews_element is not None:
                #     reviews_txt = reviews_element.find('span', attrs={'class':'clsRatingCounts'})
                #     reviews = reviews_txt.text.split('&')[1].strip().split(" ")[0]
                #     result['reviews'] = reviews
                # else:
                #     result['reviews'] = ""
                
                #Bank offers
                # offers_element = driver.find_element(By.CLASS_NAME, 'mo_box_offer clsBankOffer')
                # print(offers_element)
                # break
                results.append(result)
                counter +=1
    
    print(results)
    # return results

scrape_vijaysales_search()