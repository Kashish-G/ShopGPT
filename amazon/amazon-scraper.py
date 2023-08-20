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

def scrape_amazon_search():
    results = []

    user_query = input('Enter a product name: ')
    page = 1


    while page!=2:
        base_url = f'https://www.amazon.in/s?k={user_query}&page={page}'
        useragent = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

        web_page = requests.get(base_url, headers=useragent)
        web_page.raise_for_status()
        soup = BeautifulSoup(web_page.content, 'html.parser')

        product_url = soup.find_all('a', attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})

        counter = 0
        if product_url is None:
            print('Product url Not Found!')
        else:
            for i in product_url:
                if counter >=5:
                    break
                # final_url = product_url_list.append('https://www.amazon.in'+ i.get('href'))
                
                #EACH_PRODUCT_LINKS
                link =('https://www.amazon.in'+ i.get('href'))

                new_webpage = requests.get(link, headers=useragent)
                new_soup = BeautifulSoup(new_webpage.content, 'html.parser')
                

                #PRODUCT_TITLES
                product_names = new_soup.find_all('span', attrs={'id':'productTitle'})
                for name in product_names:
                    name_txt = name.get_text()
                    title = name_txt.strip()
                
                #PRODUCT_PRICES
                price_text = new_soup.find('span', attrs={'class':'a-price-whole'}).text
                price = "₹"+price_text
                
                #ASIN_NO.
                splitting_asin = link.split('dp')
                a = splitting_asin[1]
                slicing = a[1:13:1]
                modifying1 = slicing.removeprefix("2F")
                asin = modifying1.removesuffix('/r')

                #RATINGS
                ratings_txt = new_soup.find('div', attrs={'id':'averageCustomerReviews'})
                if ratings_txt is not None:
                    rating = ratings_txt.find('span', attrs={'class':'a-size-base a-color-base'}).text.strip()
                else:
                    rating = "No rating"

                #ALL_REVIWES
                reviews_element = new_soup.find('a', attrs={'id':'askATFLink'})
                if reviews_element is not None:
                    reviews = new_soup.find('a', attrs={'id':'askATFLink'}).text.strip().split(" ")[0]
                else:
                    reviews = 'No reviews'

                #IMAGE_URLs
                img_div = new_soup.find('div', attrs={'class':'imgTagWrapper'})
                img_tag = img_div.find_all('img', attrs={'id': 'landingImage'})
                for img in img_tag:
                    img_url = img.get('src')

                #CUT_PRICES
                cut_prices_div = new_soup.find('div', attrs={'class':'a-section a-spacing-small aok-align-center'})
                if cut_prices_div is not None:
                    cut_prices_span = cut_prices_div.find('span', attrs={'class':'a-offscreen'})
                    cut_price = cut_prices_span.text
                else:
                    cut_price = ""

                #BANK_OFFERS_NUMBERS (OFFER or OFFERS)
                bank_offer_num = new_soup.find('div', attrs={'id':'itembox-InstantBankDiscount'})
                if bank_offer_num is not None:
                    bank_offer_num_txt = bank_offer_num.find('a', attrs={'class': 'a-size-base a-link-emphasis vsx-offers-count'}).string.strip().split(" ")[1]
                else:
                    bank_offer_num_txt = ""

                #FINDING_BANK_OFFER_OF_EACH_PRODUCT
                bank_offer_url = f"https://www.amazon.in/hctp/vsxoffer?asin={asin}&deviceType=web&offerType=InstantBankDiscount&buyingOptionIndex"
                time.sleep(2)
                request_bank_offer = requests.get(bank_offer_url, headers=useragent)
                request_bank_offer.raise_for_status()
                soup_bank_offer = BeautifulSoup(request_bank_offer.content, 'html.parser')
                
                #PRITNTING_BANK_OFFER_ACCORDING_TO_"OFFERS" & "OFFER"
                if bank_offer_num_txt == 'offers':
                    bank_offers =  soup_bank_offer.find_all('p', attrs={'class':'a-spacing-mini a-size-base-plus'})
                    for offer in bank_offers:
                        offers_text = offer.get_text()
                else:
                    bank_offer = soup_bank_offer.find_all('h1', attrs={'class':'a-size-medium-plus a-spacing-medium a-spacing-top-small'})
                    for offers in bank_offer:
                        offer_txt = offers.get_text()
                        offers_text = offer_txt.strip()                
               

                result = {'platform': "Amazon", "title": title, "price":price, "cut_price":cut_price, 'href':link, "img_url":img_url, "offers":offers_text, "rating":rating, "reviwes":reviews}
                results.append(result)

                #coupons
                coupon_price_list = []
                actual_price  = result['price'].replace(",", "").removeprefix('₹').removesuffix('.')
                price_int = int(actual_price)
                print(price_int)
                coupon_price_float = price_int * 0.025
                print(coupon_price_float)
                coupon_price_list.append(str(round(coupon_price_float)))
                print(coupon_price_list)
                
                coupon_price_singal_digit = []
                for i in coupon_price_list:
                    for char in i:
                        coupon_price_singal_digit.append(char)
                coupon_price_val = coupon_price(coupon_price_singal_digit)
                result['coupon_val'] = coupon_price_val

                counter +=1

        page +=1
        print(results)
scrape_amazon_search()
