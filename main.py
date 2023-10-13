import re
from selenium import webdriver
from bs4 import BeautifulSoup
import base64
import os
import random
import string
from termcolor import colored
from time import sleep 

os.system('cls')

static_number = 0

# Initialize the WebDriver
browser = webdriver.Firefox()

# Define the URL of the website you want to scrape
main_url = 'https://liveuamap.com/'  # Replace with the actual URL

# Send an HTTP GET request to the main URL
browser.get(main_url)

# Get the HTML content of the page
html_content = browser.page_source

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Define a regular expression pattern for the desired links
pattern = re.compile(r'https://[a-zA-Z]+\.liveuamap\.com$')  # Updated pattern

# Create a list named "urls" to store the matching links
urls = []

# Extract and add links matching the pattern to the "urls" list
for link in soup.find_all('a', href=pattern):
    url = link.get('href')
    if not url in urls:
        urls.append(url)

# Loop through the extracted URLs and perform the image scraping logic for each URL
for url in urls:

    number = 0

    # Open the website in the browser
    browser.get(url)

    # Wait for the page to load completely (you can adjust the wait time as needed)
    browser.implicitly_wait(30)

    # Get the page source after the page has loaded
    page_source = browser.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the <div> with the class "leaflet-pane leaflet-marker-pane"
    marker_pane = soup.find('div', class_='leaflet-pane leaflet-marker-pane')

    # Extract <img> elements within the "leaflet-marker-pane" <div>
    try:
        img_elements = marker_pane.find_all('img')
    except:
        print(f'{colored("Failed to scrape icons from", "green")} {colored(url, "light_blue")}')
        continue

    # Define a directory to save the SVG files
    output_directory = 'icons'

    # Create the directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(f"{output_directory}\\unknown_images", exist_ok=True)

    # Maintain a set to track unique src values
    unique_src_set = set()

    # Extract the src and class attributes from each <img> element
    for img in img_elements:
        src = img['src']
        class_attr = img['class']

        # Check if the src value is already in the set (a duplicate)
        if src in unique_src_set:
            continue

        # Add the src to the set to mark it as seen
        unique_src_set.add(src)

        # Decode the base64 data and remove the prefix
        if src.startswith('data:image/svg+xml;base64,'):
            base64_data = src.replace('data:image/svg+xml;base64,', '')
            decoded_svg = base64.b64decode(base64_data)

            blacklist = [
                'leaflet-marker-icon',
                'leaflet-zoom-hide',
                'leaflet-interactive'
            ]

            # Extract the third element from the list of classes or generate a random string
            bomb_class = class_attr[1] if len(class_attr) > 2 else None

            if bomb_class in blacklist:
                bomb_class = None

            # Generate a unique file name based on the "bomb" class
            random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            filename = f"{bomb_class}.svg" if bomb_class else f"unknown_images\\{random_string}.svg"

            if not os.path.exists(os.path.join(output_directory, filename)):
                # Save the SVG data to a file
                with open(os.path.join(output_directory, filename), 'wb') as svg_file:
                    svg_file.write(decoded_svg)
                number += 1

    static_number += number
    print(f'{colored("Scraped", "green")} {colored(number, "yellow")} {colored("icons from", "green")} {colored(url, "light_blue")}')
    sleep(5)


# Close the browser
browser.quit()

print("")
print(f'{colored("Finished Downloading! Downloaded:", "green")} {colored(static_number, "yellow")} {colored("icons in total.", "green")}')