import requests, re, openpyxl
from bs4 import BeautifulSoup

# URL of the True Citrus product page
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

# Define a regex pattern to extract the quantity (ct or oz) and price from the option text
regex_pattern = r'(\d+(?:\.\d+)?\s*(?:ct|oz)|Single pk|Case pk \(\d+\))\s*-.*\$(\d+\.\d{2})'

# Find all product containers
product_containers = soup.find_all('div', class_='col-lg-3 col-md-4 col-sm-6 col-6')  # Modify the class based on inspection

for product in product_containers:
    # Extract product name
    product_name = product.find('p', class_='fw-semibold mb-2')
    if product_name:
        product_name = product_name.text.strip()
    else:
        product_name = "No name found"

    # Skip products with "bundle" or "tote" in the name
    if "bundle" in product_name.lower() or "tote" in product_name.lower():
        continue

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
            # Apply the regex to extract quantity and price
            match = re.search(regex_pattern, option_text)
            if match:
                quantity = match.group(1)  # e.g., "32ct", "Single pk", or "Case pk (10)"
                price = match.group(2)    # e.g., "5.59" or "38.00"
                break  # Stop once the first valid option is found
        else:
            quantity = "No quantity found"
            price = "No price found"
    else:
        quantity = "No quantity found"
        price = "No price found"

    # Clean and process quantity
    if "ct" in quantity:
        quantity_value = int(re.search(r'\d+', quantity).group(0))  # Extract numeric part
        price_per_count = round(float(price) / quantity_value, 2)
        price_per_ounce = None  # Not applicable for count-based products
    elif "oz" in quantity:
        quantity_value = float(re.search(r'\d+(\.\d+)?', quantity).group(0))  # Extract numeric part
        price_per_ounce = round(float(price) / quantity_value, 2)
        price_per_count = None  # Not applicable for ounce-based products
    elif "Single pk" in quantity:
        quantity_value = 1  # Default value for single packs
        price_per_count = round(float(price), 2)
        price_per_ounce = None  # Not applicable for single packs
    elif "Case pk" in quantity:
        quantity_value = int(re.search(r'\d+', quantity).group(0))  # Extract case size
        price_per_count = round(float(price) / quantity_value, 2)
        price_per_ounce = None  # Not applicable for case packs
    else:
        quantity_value = 1  # Fallback for unexpected cases
        price_per_count = None
        price_per_ounce = None

    # Format data with $ symbol (if applicable)
    price_formatted = f"${float(price):.2f}"
    price_per_count_formatted = f"${price_per_count:.2f}" if price_per_count else "N/A"
    price_per_ounce_formatted = f"${price_per_ounce:.2f}" if price_per_ounce else "N/A"

    # Store the scraped and calculated data
    products_data.append([product_name, price_formatted, quantity_value, price_per_count_formatted, price_per_ounce_formatted])

# Create a new Excel workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "True Citrus Data"

# Add header row
headers = ["Product Name", "Total Price", "Quantity", "Price Per Count", "Price Per Ounce"]
ws.append(headers)

# Add product data to the worksheet
for product in products_data:
    ws.append(product)

# Save the workbook
file_name = "TrueCitrusData.xlsx"
wb.save(file_name)
print(f"Data successfully written to {file_name}")
