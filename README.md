# Minified-Civitai
A python script that allows you to download and manage Civitai model pages as either minified html pages, markdown pages, or just json objects.

The basic usage is to call `get.py` and pass it Civitai model IDs (found in the URL of the model page). It will then download the data needed to recreate a minified version of the website. It also creates a cache file that stores all of the images as base64 strings to allow embedding of images into the html files. The cache file may get very large, I do not recommend trying to open it after you have downloaded a lot of images as it will probably crash your text editor.

This is my personal script and was not created with the intent on publishing but after request I have shared it. It relies on Civitai not altering their website and may stop functioning at any time. **Use this script at your own risk, you bare all responsibility for using it.**

# Usage
A recommended example using `4201` and `4384` as example model pages you would like to download (`-p` is used to output which model it is working on downloading):

```shell
python get.py 4201 4384 -p
```

If you only pass one model, the program will create sub-folders and output to the corresponding folder based on the model type. If you pass more than one model, the program will create a zip file with the output and a `merged.json` file that can be used as input, along with the `-u` argument, to update previously downloaded models.

For example, the following will redownload `4201` `4384` and recreate their output files:

```shell
python get.py merged.json -u -p
```

You can also add additional models and update existing pages by including more model ids:

```shell
python get.py merged.json 5396 -u -p
```

Run `python get.py -?` for further explanation of the available arguments.