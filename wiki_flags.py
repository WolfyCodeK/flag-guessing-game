import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Initialize an empty DataFrame to hold all flags data
all_flags_df = pd.DataFrame()

# SCRIPT 1: Sovereign States Flags
url1 = "https://en.wikipedia.org/wiki/List_of_national_flags_of_sovereign_states"
response1 = requests.get(url1)
soup1 = BeautifulSoup(response1.content, 'html.parser')
table1 = soup1.find('table', {'class': 'wikitable'})
country_names = []
flag_images = []

for row in table1.find_all('tr')[1:]:  # Skip header row
    cols = row.find_all('td')
    if len(cols) > 1:
        country_name = cols[0].text.strip()
        image = cols[0].find('img')
        flag_image_url = "https:" + image['src'] if image else None
        country_names.append(country_name)
        flag_images.append(flag_image_url)

flags_df1 = pd.DataFrame({'Name': country_names, 'URL': flag_images})
all_flags_df = pd.concat([all_flags_df, flags_df1], ignore_index=True)

# SCRIPT 2: Micronations Flags
# url2 = "https://en.wikipedia.org/wiki/Flags_of_micronations"
# response2 = requests.get(url2)
# soup2 = BeautifulSoup(response2.content, 'html.parser')
# flags_data2 = []
# gallery_boxes = soup2.find_all('li', class_='gallerybox')

# for box in gallery_boxes:
#     flag_img = box.find('img')
#     if flag_img:
#         flag_url = 'https:' + flag_img['src']
#         name_link = box.find('div', class_='gallerytext').find('a')
#         micronation_name = name_link.get_text(strip=True) if name_link else None
#         flags_data2.append((micronation_name, flag_url))

# flags_df2 = pd.DataFrame(flags_data2, columns=['Name', 'URL'])
# all_flags_df = pd.concat([all_flags_df, flags_df2], ignore_index=True)

# SCRIPT 3: City Flags
url3 = 'https://en.wikipedia.org/wiki/Lists_of_city_flags'
response3 = requests.get(url3)
soup3 = BeautifulSoup(response3.text, 'html.parser')
city_names = []
flag_urls = []

flags3 = soup3.find_all('img')
for img in flags3:
    flag_url = 'https:' + img['src']
    city_name = img.get('alt', 'No name')
    city_names.append(city_name)
    flag_urls.append(flag_url)

flags_df3 = pd.DataFrame({'Name': city_names, 'URL': flag_urls})
all_flags_df = pd.concat([all_flags_df, flags_df3], ignore_index=True)

# SCRIPT 4: Dependent Territories Flags
url4 = 'https://en.wikipedia.org/wiki/Gallery_of_flags_of_dependent_territories'
response4 = requests.get(url4)
soup4 = BeautifulSoup(response4.content, 'html.parser')
gallery_items = soup4.find_all('li', class_='gallerybox')
names = []
image_urls = []

for item in gallery_items:
    img_tag = item.find('img')
    if img_tag:
        img_url = 'https:' + img_tag['src']
        image_urls.append(img_url)
        text_div = item.find('div', class_='gallerytext')
        if text_div:
            flag_text = text_div.get_text(strip=True)
            names.append(flag_text)  # Capture the entire text
        else:
            names.append(None)
    else:
        image_urls.append(None)

# Add additonal flags not found on wiki page
names.append('Guadeloupe (unofficial)')
image_urls.append('https://upload.wikimedia.org/wikipedia/commons/e/e7/Unofficial_flag_of_Guadeloupe_%28local%29.svg')

names.append('Guadeloupe (official)')
image_urls.append('https://upload.wikimedia.org/wikipedia/commons/d/d1/Flag_of_Guadeloupe_%28UPLG%29.svg')

names.append('French Guiana')
image_urls.append('https://upload.wikimedia.org/wikipedia/commons/2/29/Flag_of_French_Guiana.svg')

names.append('Mayotte')
image_urls.append('https://upload.wikimedia.org/wikipedia/commons/b/bf/Coat_of_Arms_of_Mayotte.svg')

names.append('Reunion')
image_urls.append('https://upload.wikimedia.org/wikipedia/commons/8/8e/Proposed_flag_of_R%C3%A9union_%28VAR%29.svg')


flags_df4 = pd.DataFrame({'Name': names, 'URL': image_urls})
all_flags_df = pd.concat([all_flags_df, flags_df4], ignore_index=True)

# Clean up names by removing prefixes and unnecessary articles
all_flags_df['Name'] = (
    all_flags_df['Name']
    .str.replace(r'(?i)^Flag\s*of\s*', '', regex=True)  # Remove "Flag of" (case insensitive)
    .str.replace(r'(?i)^\s*the\s*', '', regex=True)  # Remove "the" at the beginning (case insensitive)
    .str.replace(r'(?i)^\s*Flag\s*', '', regex=True)  # Remove "Flag" at the beginning (case insensitive)
    .str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with a single space
    .str.strip()  # Remove any leading or trailing spaces
)

# Additional processing to handle unwanted entries
def clean_city_name(name):
    if 'Most populated city in the world' in name:
        # If it contains the phrase, extract the part after the semicolon
        name = name.split(';')[-1].strip()  # Get the last part and strip whitespace
    # If the name contains a comma, split and take the first part
    if ',' in name:
        name = name.split(',')[0].strip()  # Return the part before the comma
    return name

all_flags_df['Name'] = all_flags_df['Name'].apply(clean_city_name)

# Filter to only keep valid flag entries
unwanted_phrases = [
    'Wikipedia',
    'Wikimedia Foundation',
    'Powered by MediaWiki',
    'No name',
    'copyright',
    'most populated city',
    'free encyclopedia',
    'flag of the',
    'flag of', 
    'Flags of',
    'flag', 
]

# Check if a name is valid
def is_flag_entry(name):
    # Check if the name is valid by looking for keywords indicating a flag
    if any(phrase.lower() in name.lower() for phrase in unwanted_phrases):
        return False
    if len(name) < 3:  # Length check to avoid very short names
        return False
    return True

# Apply the filtering function
all_flags_df = all_flags_df[all_flags_df['Name'].apply(is_flag_entry)]

if not os.path.exists("csv"):
    os.makedirs("csv")

# Save the combined DataFrame to a single CSV file
all_flags_df.to_csv('csv/all_flags.csv', index=False)
print("Data has been saved to 'all_flags.csv'.")
