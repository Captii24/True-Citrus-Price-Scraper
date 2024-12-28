import requests
import re
from bs4 import BeautifulSoup

# URL of the True Citrus product page (adjust as needed)
url = 'https://www.truecitrus.com/collections/all-products'

# Send a GET request to fetch the content of the page
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Page fetched successfully!")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# List to store scraped product data
products_data = []

# Define a regex pattern to extract the quantity (oz or ct) and price from the option text
# The pattern looks for digits followed by "ct" or "oz", followed by " - $<price>"
regex_pattern = r'(\d+(?:\.\d+)?)\s*(ct|oz)\s*-.*\$(\d+\.\d{2})'

# Find all product containers (adjust the selector based on inspection)
product_containers = soup.find_all('div', class_='col-lg-3 col-md-4 col-sm-6 col-6')  # Modify the class based on inspection

for product in product_containers:
    # Extract product name (as before)
    product_name = product.find('p', class_='fw-semibold mb-2')
    if product_name:
        product_name = product_name.text.strip()
    else:
        product_name = "No name found"

    # Extract the price and quantity from the select element and its options
    select_element = product.find('select', class_='mb-2 xmRK4 form-select')
    if select_element:
        # Find all option tags inside the select element
        options = select_element.find_all('option')
        for option in options:
            # Skip "select size" and "out of stock" options
            if "select size" in option.text.lower() or "out of stock" in option.text.lower():
                continue
            
            option_text = option.text.strip()
            # Apply the regex to extract quantity (oz or ct) and price
            match = re.search(regex_pattern, option_text)
            if match:
                quantity = match.group(1) + match.group(2)  # e.g., "32ct" or "10.6oz"
                price = match.group(3)  # e.g., "5.59"
                break  # Stop once the first valid option is found
        else:
            quantity = "No quantity found"
            price = "No price found"
    else:
        quantity = "No quantity found"
        price = "No price found"

    # Print the result for this product
    print(f"Product: {product_name}, Price: ${price}, Quantity: {quantity}")
