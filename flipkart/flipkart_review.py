import requests
from bs4 import BeautifulSoup
import csv
import time
from textblob import TextBlob

url = "https://www.flipkart.com/primebook-4g-android-based-mediatek-mt8788-4-gb-64-gb-emmc-storage-prime-os-thin-light-laptop/product-reviews/itmecb7e931de990?pid=COMGH2NKYVZCVXAW&lid=LSTCOMGH2NKYVZCVXAWAYX3II&marketplace=FLIPKART"

# Send GET request to the URL
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find the total number of review pages
total_pages = int(soup.find("div", class_="_2MImiq _1Qnn1K").span.string.split()[-1])

reviews = []

# Iterate through all review pages
for page in range(1, total_pages+1):
    print(f"Scraping page {page}...")
    page_url = url + f"&page={page}"
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all review containers on the page
    review_containers = soup.find_all("div", class_="_1AtVbE")
    
    # Extract review text and rating from each container
    for container in review_containers:
        review_text_element = container.find("div", class_="t-ZTKy")
    
        # Find rating element with different class names
        rating_element = container.find("div", class_=["_3LWZlK _1rdVr6 _1BLPMq", "_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq","_3LWZlK"])
    
        # Check if the required elements exist
        if review_text_element and rating_element:
            review_text = review_text_element.get_text(strip=True)
            rating = rating_element.text
            reviews.append({"review_text": review_text, "rating": rating})
        
    # Add a delay to avoid overwhelming the server
    time.sleep(2)

# Perform sentiment analysis and classify feedback as good, neutral, or bad
total_sentiment_score = 0
for review in reviews:
    text = review["review_text"]
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    rating = int(review["rating"])

    if rating >= 4:
        sentiment_label = "Good"
    elif rating >= 3:
        sentiment_label = "Neutral"
    else:
        sentiment_label = "Bad"

    review["sentiment_score"] = sentiment_score
    review["sentiment_label"] = sentiment_label

    total_sentiment_score += sentiment_score

# Calculate the average sentiment score
average_sentiment_score = total_sentiment_score / len(reviews)

# Classify the overall sentiment based on the average score
if average_sentiment_score >= 0.4:
    overall_sentiment = "Good"
elif average_sentiment_score >= 0.2:
    overall_sentiment = "Neutral"
else:
    overall_sentiment = "Bad"

# Write the updated reviews to a CSV file
with open("reviews_with_sentiment.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Review", "Rating", "Sentiment Score", "Sentiment Label"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for review in reviews:
        writer.writerow({
            "Review": review["review_text"],
            "Rating": review["rating"],
            "Sentiment Score": review["sentiment_score"],
            "Sentiment Label": review["sentiment_label"]
        })

print("Sentiment analysis complete. Updated reviews saved to reviews_with_sentiment.csv.")
print("Overall sentiment:", overall_sentiment)
