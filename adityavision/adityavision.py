import requests
from bs4 import BeautifulSoup

def scrape_adityavision_search():
    results = []
    search_query = input("Enter the search query: ")
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
        price_list = []
        if price_element:
            # Remove leading and trailing whitespace
            price = price_element.text.replace('From',"").strip()
            result['price']=price
            price_list.append(price)
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
            cut_price = cut_price_element_two.text.strip()
            result['cut_price']=cut_price

        result["platform"] = "Aditya Vision"
        results.append(result)
        counter += 1
        
    print(results)
        
# Example usage
scrape_adityavision_search()
