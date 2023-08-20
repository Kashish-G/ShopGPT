from bs4 import BeautifulSoup
import requests
import time


def scrape_snapdeal_search():
    user_query = input('Enter a product name: ')
    base_url = f"https://www.snapdeal.com/search?keyword={user_query}"
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
        result = {'href':link}

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
            result['price'] = price

        # BANK OFFERS
        offers_div_one = new_soup.find_all(
            'div', attrs={'class': "offerBlock clearfix"})
        if offers_div_one is not None:
            for i in offers_div_one:
                offers_text = i.get_text()
                offer_pure_text = offers_text.strip().replace('T&C', "")
                offers = offer_pure_text.strip()
                result['offers'] = offers
        else:
            result['offers'] = []

        # IMAGE_URLs
        img_ul_tag = new_soup.find(
            'ul', attrs={'id': 'bx-slider-left-image-panel'})
        img_tag = img_ul_tag.find('img').get('bigsrc')
        img_url = img_tag
        result['img_url'] =img_url

        #cut_price
        cut_price_element = new_soup.find('div', attrs={'class':'pdpCutPrice'})
        cut_price = cut_price_element.text.split(" ")[0].removesuffix("(Inclusive").strip().removeprefix('MRP').strip().removeprefix('Rs.').strip()
        result['cut_price'] = cut_price

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

    print(results)
scrape_snapdeal_search()