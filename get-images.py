import os
import csv
import requests
import re
import shutil

# Define the path to the CSV file and the folders
csv_file_path = "flag_image_urls.csv"
flags_folder = "flags"
additional_flags_folder = "additional flags"

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

# Function to copy files from one directory to another
def copy_files(src_directory, dest_directory):
    for filename in os.listdir(src_directory):
        src_file_path = os.path.join(src_directory, filename)
        dest_file_path = os.path.join(dest_directory, filename)
        try:
            if os.path.isfile(src_file_path):
                shutil.copy2(src_file_path, dest_file_path)  # Copy files
                print(f"Copied {src_file_path} to {dest_file_path}")
        except Exception as e:
            print(f"Failed to copy {src_file_path}: {e}")

# Copy additional flags into the flags folder
if os.path.exists(additional_flags_folder):
    copy_files(additional_flags_folder, flags_folder)

# Function to generate a valid filename
def generate_valid_filename(flag_name):
    # Use regex to keep only letters, numbers, spaces, and hyphens; remove other special characters
    valid_flag_name = re.sub(r'[^A-Za-z0-9 \-]+', '', flag_name)  # Remove special characters, keep spaces and hyphens
    return valid_flag_name

# Read the flag data from the CSV file
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row

    for row in reader:
        flag_name = row[0]
        image_url = row[1]

        # Generate a valid filename
        valid_flag_name = generate_valid_filename(flag_name)
        output_path = os.path.join(flags_folder, f"{valid_flag_name}.png")

        try:
            # Send a GET request to the image URL
            response = requests.get(image_url)
            response.raise_for_status()  # Check if the request was successful

            # Save the image to the specified path
            with open(output_path, "wb") as image_file:
                image_file.write(response.content)

            print(f"Image successfully saved to {output_path}")
        except Exception as e:
            print(f"Failed to download or save {flag_name}: {e}")

print("Download process completed.")
