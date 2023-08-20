import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

def scrape_shopcules_search():   
    search_query = input("Enter the search query: ")
    base_url = "https://www.shopclues.com/search"
    useragent = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    params = {"q": search_query}

    response = requests.get(base_url, params=params, headers=useragent)
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
        result = {"id":counter, "platform":"Shopclues",'title':title}

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
        result['after 3.00%'] = coupon_price_list
        result['coupon_val'] = coupon_price_val
        results.append(result)
        counter += 1
        # break   
    
    print(results)
if __name__ == '__main__':
    scrape_shopcules_search()