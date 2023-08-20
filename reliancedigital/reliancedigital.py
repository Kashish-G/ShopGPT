from bs4 import BeautifulSoup
import requests
import time

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

def scrape_reliance_digital_search():
    user_query = input("Enter a product name: ")
    base_url = f"https://www.reliancedigital.in/search?q={user_query}"
    time.sleep(1)
    useragent = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    web_page = requests.get(base_url, headers=useragent)
    web_page.raise_for_status()
    soup = BeautifulSoup(web_page.content, 'html.parser')

    product_url_div = soup.find('div', attrs={'class':"pl__container"})
    half_url =  product_url_div.find_all("a", attrs={'attr-tag':'anchor'})

    counter = 0

    results = []
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
                
        if reviews_text == [] or reviews_text == " ":
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
        print(coupon_price_list)

        coupon_price_singal_digit = []
        for i in coupon_price_list:
            for char in i:
                coupon_price_singal_digit.append(char)
        print(coupon_price_singal_digit)
        coupon_price_val = coupon_price(coupon_price_singal_digit)
        print(coupon_price_val)
        result['coupon_val'] = coupon_price_val
            
        result["platform"] = "Reliance Digital"
        results.append(result)

        counter += 1
      
    print(results)
scrape_reliance_digital_search()
            



