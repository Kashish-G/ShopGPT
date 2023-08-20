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

def scrape_flipkart_search():
    query = input("Enter the search query: ")
    base_url = "https://www.flipkart.com/search"
    params = {"q": query}

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    search_results = soup.find_all("div", {"class": "_1AtVbE"})

    counter = 0  # Counter to keep track of non-advertisement products
    results = []

    for result in search_results:
        if counter >= 10:
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
                        'id': counter,
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

                price_list = []
                price_element = result.find("div", {"class": "_30jeq3"})
                if not price_element:
                    continue

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
                    'id':counter,
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
                print(coupon_price_list)

                coupon_price_singal_digit = []
                for i in coupon_price_list:
                    for char in i:
                        coupon_price_singal_digit.append(char)
                print(coupon_price_singal_digit)
                coupon_price_val = coupon_price(coupon_price_singal_digit)
                
                results[-1]['after 5%'] = coupon_price_list
                results[-1]['coupon_val'] = coupon_price_val
                
    print(results)

scrape_flipkart_search()