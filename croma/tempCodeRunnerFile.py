from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Selenium WebDriver
driver = webdriver.Chrome()
search_query = input("Enter the search query: ")
url = "https://www.croma.com/searchB?q=" + search_query + "%3Arelevance&text=" + search_query
driver.get(url)

# Wait for the product elements to be loaded
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cp-product.typ-plp')))

# Extract the data
start_link = 'https://www.croma.com'

product_elements = driver.find_elements(By.CSS_SELECTOR, 'div.cp-product.typ-plp')
for product in product_elements:
    wait.until(EC.visibility_of(product.find_element(By.CSS_SELECTOR, 'h3.product-title.plp-prod-title')))
    rest_link = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    name = product.find_element(By.CSS_SELECTOR, 'h3.product-title.plp-prod-title').text
    price = product.find_element(By.CSS_SELECTOR, 'span.amount').text
    print("Name:", name)
    print("Price:", price)
    print("Href:", start_link + rest_link)
    print("-" * 40)

# Close the WebDriver
driver.quit()
