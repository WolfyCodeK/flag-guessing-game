import os
import csv
import requests
from cairosvg import svg2png

# Define the path to the CSV file and the folders
csv_file_path = "csv/all_flags.csv"
flags_folder = "flags"

# Create the flags folder if it doesn't exist
os.makedirs(flags_folder, exist_ok=True)

# Function to delete all contents of a directory
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # Remove files and links
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Remove empty directories
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

# Clear the flags folder
clear_directory(flags_folder)

# Function to download and handle images
def download_and_convert_image(url, output_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if url.lower().endswith('.svg'):
        try:
            svg2png(bytestring=response.content, write_to=output_path)
            print(f"SVG converted and saved as PNG to {output_path}")
        except Exception as e:
            print(f"Failed to convert SVG to PNG for {url}: {e}")
    else:
        with open(output_path, "wb") as image_file:
            image_file.write(response.content)
        print(f"Image successfully saved to {output_path}")

# Read the flag data from the CSV file
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row

    for row in reader:
        flag_name = row[0]
        image_url = row[1]

        output_path = os.path.join(flags_folder, f"{flag_name}.png")

        try:
            download_and_convert_image(image_url, output_path)
        except Exception as e:
            print(f"Failed to download or save {flag_name}: {e}")

print("Download process completed.")
