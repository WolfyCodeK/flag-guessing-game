import csv
import re
import requests
from bs4 import BeautifulSoup

# Fetch the webpage
url = "https://flages.fandom.com/wiki/List_of_flags"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Prepare a list to store flag names and image URLs
flag_data = []

# Find all flag entries
flag_rows = soup.find_all("tr")

# Loop through each row to extract flag names and image URLs
for row in flag_rows:
    cells = row.find_all("td")
    if len(cells) >= 2:
        # Extract flag name and remove "Flag of" part
        flag_name = cells[0].get_text(strip=True).replace("Flag of ", "")
        flag_name = flag_name.replace("—", "-")
        flag_name = flag_name.replace('"', '').replace("'", "")
        flag_name = re.sub(r'[^A-Za-z0-9 \-]+', '', flag_name)
        
        # Find the image URL from the <a> tag with class "image"
        a_tag = cells[1].find("a", class_="image")
        if a_tag and 'href' in a_tag.attrs:
            img_url = a_tag['href']  # Use the URL from the <a> tag
            flag_data.append([flag_name, img_url])  # Append to the list
        else:
            print(f"Image not found for {flag_name}")

# Write the flag data to a CSV file
csv_file_path = "flag_image_urls.csv"
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Flag Name", "Image URL"])  # Write header
    writer.writerows(flag_data)  # Write flag data

print(f"Saved flag image URLs to {csv_file_path}")
