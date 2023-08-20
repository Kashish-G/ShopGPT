import json
import requests
import time
import random
import nltk
from nltk.tokenize import word_tokenize


# Load the intents from intents.json
with open('chatbot/intents.json') as file:
    intents = json.load(file)

# Function to handle the "product_inquiry" intent
def handle_product_inquiry(query):
    # Prepare the request payload
    payload = {'query': query}

    # Call the API to fetch product results
    response = requests.post('http://localhost:5000/api/search', json=payload)

    if response.status_code == 200:
        api_response = response.json()
        if api_response['results']['status'] == 'success':
            products = api_response['results']['data']
            if products:
                # Generate a response combining the API results and the predefined response
                response_text = f"Here are some products matching your query:\n"
                for product in products:
                    response_text += f"  Name: {product['title']}\n"
                    response_text += f"  Price: {product['price']}\n"
                    response_text += f"  Available on {product['platform']}\n"
                    response_text += f"  More Info: {product['href']}\n"
                return response_text
            else:
                return "I'm sorry, but I couldn't find any products matching your query."
        else:
            return "I'm sorry, but the API request was not successful."
    else:
        return "I'm sorry, but I couldn't fetch the product information at the moment. Please try again later."

# Function to handle responses from other intents
def handle_other_responses(intent):
    responses = intent['responses']
    response = random.choice(responses)
    typing_print(response)
    print()

# Function to print text with typing effect
def typing_print(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.05)  # Adjust the delay (in seconds) for the typing effect
    print()

# Chat loop
while True:
    user_input = input("Please enter your query: ")
    user_tokens = word_tokenize(user_input.lower())

    # Check if the user input matches any intent
    matched_intent = next((intent for intent in intents if any(pattern.lower() in user_tokens for pattern in intent['patterns'])), None)

    if matched_intent:
        if matched_intent['tag'] == 'product_inquiry':
            query = user_input
            response = handle_product_inquiry(query)
            print(response)
        elif matched_intent['tag'] == 'goodbye':
            handle_other_responses(matched_intent)
            break
        else:
            handle_other_responses(matched_intent)
    else:
        # If no intent is matched, respond with fallback response
        fallback_intent = next((intent for intent in intents if intent['tag'] == 'fallback'), None)
        handle_other_responses(fallback_intent)
