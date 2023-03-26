# Minified-Civitai
A python script that allows you to download and manage Civitai model pages as either minified html pages, markdown pages, or just json objects.

The basic usage is to call `get.py` and pass it Civitai model IDs (found in the URL of the model page). It will then download the data needed to recreate a minified version of the website. It also dowloads all images from the model page into a image_cache subfolder.

By default it also compiles all saved model pages in one `merged.json` file and creates a `version_files.json` file that stores a link from Civitai IDs to the actual model filenames/hashes.

This is my personal script and was not created with the intent on publishing but after request I have shared it. It relies on Civitai not altering their website and may stop functioning at any time. **Use this script at your own risk, you bear all responsibility for using it.**

Also note that the html files use an experimental CSS feature for displaying user comments that is only available on FireFox and you need to specifically opt into in order to use. It's called [masonry layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Masonry_Layout). If you do not opt into using this feature or use a different browser the user comments on the page will have gaps between them.

# Usage
A recommended example using `4201` and `4384` as example model pages you would like to download (`--print` is used to output which model it is working on downloading while the script is running):

```shell
python get.py 4201 4384 --print
```

The program will create sub-folders and output to the corresponding folder based on the model type and file type you are trying to generate. to update previously downloaded models you can pass in the `merged.json` file as an input, along with the `--update` argument which will force it to redownload models found in any JSON files it is given.

For example, the following will redownload `4201` `4384` and recreate their output files:

```shell
python get.py merged.json --update --print
```

You can also add additional models and update existing pages by including more model ids:

```shell
python get.py merged.json 5396 --update --print
```

**Run `python get.py -?` for further explanation of the available arguments.**
