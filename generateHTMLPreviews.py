"""
READ ME

This code assumes its being run from a folder 'stable-diffusion-webui\custom-files\minified-civitai'
If you are copying this directory structure you will probably want a .gitignore file located in custom-files that only contains '*' to remove the folder and subfolders from the automatic1111 git repository.
This code also assumes all of the downloaded minified civitai webpages are located in respective subfolders eg: 'minified-civitai/models' etc
It then uses a relative path to find your model folders eg: '..\..\models\Stable-diffusion' should point to 'stable-diffusion-webui\models\Stable-diffusion'
Then it will create a subfolder in the models folder called 'Previews' and create an html file that uses an iframe to link back to the minified civitai page located in the corresponding minified-civitai folder eg: 'stable-diffusion-webui\custom-files\minified-civitai\models'
This way if you have mulitple versions of the same model you dont have to store mulitple large html files.
In order to create the html file it uses version_files.json to look up the expected file names of your models. If you have changed your model names you can try and use the hash to match (will take a bit) or manually edit the json file to add your existing file name to the correspoinding version.
"""

import os
import io
import json
import base64
from PIL import Image
from typing import Dict
import argparse

# Function to calculate the AutoV1 hash of the file
def model_hash_AutoV1(filename:str)->str:
	try:
		with open(filename, "rb") as file:
			import hashlib as hashlib
			m = hashlib.sha256()
			# Seek to the 100000th byte
			file.seek(0x100000)
			# Read the next 10000 bytes
			m.update(file.read(0x10000))
			# Return the first 8 characters of the hex digest
			return m.hexdigest()[0:8]
	except FileNotFoundError:
		# Return None if file not found
		return None

def model_hash_full(filename: str) -> str:
    try:
        with open(filename, "rb") as file:
            import hashlib
            m = hashlib.sha256()
            file_contents = file.read()
            m.update(file_contents)
            return m.hexdigest()
    except FileNotFoundError:
        return None

def model_hash_AutoV2(filename: str) -> str:
    try:
        with open(filename, "rb") as file:
            import hashlib
            m = hashlib.sha256()
            file_contents = file.read()
            m.update(file_contents)
            return m.hexdigest()[:10]
    except FileNotFoundError:
        return None

def model_hash_all(filename: str) -> tuple:
    try:
        with open(filename, "rb") as file:
            import hashlib
            m1 = hashlib.sha256()
            m2 = hashlib.sha256()
            file_contents = file.read()
            m1.update(file_contents[0x100000:0x110000])
            m2.update(file_contents)
            return (m1.hexdigest()[0:8], m2.hexdigest()[:10], m2.hexdigest())
    except FileNotFoundError:
        return (None, None, None)


# Get the relative path back to this directory where the html previews are saved
def reverse_relative_path(original_path:str)->str:
	# Split the path on the directory separator
	directories = original_path.split("\\")
	# Count the number of directories in the path
	num_directories = len(directories)
	# Generate the relative path by going up one directory level for each directory in the original path
	relative_path = ""
	for i in range(num_directories):
		relative_path += "..\\"
	relative_path = "http://127.0.0.1:7860"
	# Get the current running directory folder name
	current_dir_folder = "file=custom-files/" + os.path.basename(os.path.dirname(os.path.abspath(__file__))).replace("\\","/")
	# Add current running directory folder name to the relative path
	relative_path = os.path.join(relative_path,current_dir_folder).replace("\\","/")
	return relative_path

# Function to search for models in the given directory and create HTML preview files for each file with matching names 
def create_preview_pages(relative_path:str, folder, version_files:Dict, args):
	# Get the relative path back to the folder that has the HTML files which will be linked to in the newly created HTML preview files
	relative_path_to_html_files = reverse_relative_path(relative_path)
	# Tuple of file extensions to search for
	search_extensions = ('.bin', '.pt', '.safetensors', '.ckpt')
	# Keep track of files that couldn't be found in the version files object
	not_found = []
	hash_found = []
	# Loop through the files in the directory
	for root, dirs, files in os.walk(relative_path):
		for file in files:
			# Skip any file that doesn't end in an extension we care about
			if file.endswith(search_extensions):
				found_file = False
				file_hash_autov1, file_hash_autov2, file_hash_sha256 = (None, None, None)
				# Check if the file exists in the version_files dictionary ignoring case
				for key, value in version_files.items():
					if file.lower() in [val.lower() for val in value['files']]:
						found_file = True
						if key == "0" or key == 0 or value['name'] == "Ignore":
							break
						generate_html_file(relative_path_to_html_files, root, file, key, value, args)
						generate_preview(root, file, value)
						break
				if not found_file and args.find_by_hash:
					# Calculate hash of the current file
					file_hash_autov1, file_hash_autov2, file_hash_sha256 = model_hash_all(os.path.join(root, file))

					# Check if the hash exists in the version_files dictionary ignoring case (dont use autov1 because it has collision issues)
					hashes_to_find = [
						{ "hash": file_hash_sha256, "type": "SHA256" },
						{ "hash": file_hash_autov2, "type": "AutoV2" }
					]
					# Loop through all the items in the version files
					for key, value in version_files.items():
						for hash_to_find in hashes_to_find:
							# Loop through all the hashes searching for sha256 hashes
							for hash in value['hashes']:
								if hash['hash'].lower() == hash_to_find['hash'].lower() and hash['type'].lower() == hash_to_find['type'].lower():
									found_file = True
									generate_html_file(relative_path_to_html_files, root, file, key, value, args)
									generate_preview(root, file, value)
									hash_found.append(f"Hash Found: [{hash}], File: '{file}'")
									break
							if found_file:
								break
						if found_file:
							break
				if not found_file:
					out = [file]
					if file_hash_autov1:
						out.append(f'[{file_hash_autov1}]')
					if file_hash_autov2:
						out.append(f'[{file_hash_autov2}]')
					# The model was not found in the version file list, save the file to print to console later
					not_found.append(" ".join(out))
	if hash_found:
		print("Hashes Found:")
		for file in hash_found:
			print(file)
	if not_found:
		print("Not Found:")
		for file in not_found:
			print(file)

def generate_preview(root, file, value):
	if value["image"]:
		base, ext = os.path.splitext(file)
		new_file = base + '.png'
		new_file_preview = base + '.preview.png'
		new_path = os.path.join(root, new_file)
		new_path_preview = os.path.join(root, new_file_preview)
		if not os.path.exists(new_path) and not os.path.exists(new_path_preview):
			try:
				cache_file = os.path.join('image_cache', value["image"])
				if os.path.isfile(cache_file):
					with open(cache_file, 'rb') as f:
						image_data = f.read()
					f.close()

					if value["folder"].lower() == "embeddings":
						image_path = new_path_preview
					else:
						image_path = new_path
						
					# Convert image data to PNG if necessary
					with io.BytesIO(image_data) as img_buffer:
						with Image.open(img_buffer) as img:
							img.save(image_path)
			except Exception as e:
				print(f"ERROR with preview Image for {file}")
				print('An error occurred: {}'.format(e))

def generate_html_file(relative_path_to_html_files, root, file, key, value, args):
	# Create a new HTML file that will have an iframe linking to the saved preview HTML
	base, ext = os.path.splitext(file)
	new_file = base + '.html'
	new_path = os.path.join(root, 'Previews', new_file)
	os.makedirs(os.path.dirname(new_path), exist_ok=True)
	overwrite = True
	# Write the HTML file to disk if it doesnt already exist
	if overwrite == True or not os.path.exists(new_path):
		# Create the iframe src path
		iframe_src = os.path.join(relative_path_to_html_files,value["folder"],value["html"])
		html = f'<html>\n'
		html += f'\t<head>\n'
		html += f'\t\t<meta name="author" content="generatePreviews.py">\n'
		html += f'\t</head>\n'
		html += f'\t<body style="padding: 0;margin: 0;position: relative;">\n'
		html += f'\t\t<iframe src="{iframe_src}#{key}" width="100%" height="100%" style="border: none;"></iframe>\n'
		html += f'\t</body>\n'
		html += f'</html>'
		if args.print:
			print(new_path)
		with open(new_path, 'w') as f:
			f.write(html)

help_description = f'Search through the default model folders for models and then look the file name up in "versions_file.json"\n\
to find the corresponding generated preview file and then create specific html preview files that use iframes to link to the generated preview files for each model.'

help_epilog = f''

class NewlineFormatter(argparse.RawDescriptionHelpFormatter):
	def _split_lines(self, text, width):
		return text.splitlines()

# Guard statement to make sure the code is being run as the main program
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=help_description, add_help=False, epilog=help_epilog, formatter_class=NewlineFormatter)
	parser.add_argument('-f', '--find_by_hash', action='store_true', help='If the scan cannot find the model in the "versions_file.json" file, also generate a hash for the model file and search for the hash in the versions file')
	parser.add_argument('-p', '--print', action='store_true', help='Output a message with the path to any generated html files')
	parser.add_argument('-?', '--help', action='store_true', help='show this help message and exit')
	args = parser.parse_args()

	if args.help:
		# Show the help message and exit
		parser.print_help()
		exit()

	# Load json file containing the files and their hashes
	version_files = json.load(open('version_files.json'))
	# Call the function to search for files
	print("models -------------------------")
	create_preview_pages("..\..\models\Stable-diffusion", "models", version_files, args)
	print("lora ---------------------------")
	create_preview_pages("..\..\models\lora", "lora", version_files, args)
	print("hypernetwork -------------------")
	create_preview_pages("..\..\models\hypernetworks", "hypernetwork", version_files, args)
	print("embeddings ---------------------")
	create_preview_pages("..\..\embeddings", "embeddings", version_files, args)
