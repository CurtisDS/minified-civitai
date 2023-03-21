"""
READ ME

Intended to be used when upgrading to v2 which doesnt use cache.json anymore.
This code will convert the base64 strings in cache.json to individual files located in the subfolder 'image_cache/'.
After upgrading you can delete cache.json.
Alternatively you can choose to just delete cache.json and have the files redownload the next time you run get.py.
"""

import os
import json
import base64
from PIL import Image
from io import BytesIO

# Load the cache to memory
try:
	with open('cache.json', 'r') as f:
		image_cache = json.load(f)
	f.close()
except FileNotFoundError:
	exit("Not Found")

# Create variables to keep track of progress
items_length = len(image_cache)
item_index = 0

# Loop through the image cache
for key, value in image_cache.items():
	# Output the progress
	item_index += 1
	print(f"{item_index}/{items_length}")

	# Skip invalid images
	if value is None or not value.startswith("data:"):
		continue

	# Extract the file format and encoded image data from the data URI
	file_format, encoded_data = value.split(";base64,")
	file_extension = file_format.split("/")[-1]

	# Decode the Base64 data and create a PIL Image object
	decoded_data = base64.b64decode(encoded_data)
	image = Image.open(BytesIO(decoded_data))
	
	# Extract the ID from the url
	new_key = key.replace('/width=400', '').replace('https://imagecache.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/', '')
	
	# Create the image_cache subfolder if it doesn't exist
	if not os.path.exists('image_cache'):
		os.makedirs('image_cache')
	
	# Save the image
	image.save(os.path.join('image_cache', new_key), format=file_extension)