# Save fragment images to zip file from image URL

import requests
import shutil
import pandas as pd
import os
import zipfile
import datetime

today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
app = "directline"

home = os.path.expanduser("~")
os.chdir(home + "/desktop/")

td_file = pd.read_csv("directline_tag_demographics_20170706.csv")

def test_images(row):
    tag_df = row[1]

    iurl = tag_df["Image URL"]
    image_filename = iurl.split("/")[-1]

    r = requests.get(iurl, stream=True)

    with open(image_filename, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)

    with zipfile.ZipFile(app + "-fragment-images-" + today + ".zip", "a") as frag_zip:
        frag_zip.write(image_filename, compress_type=zipfile.ZIP_DEFLATED)

    os.remove(image_filename)

for row in td_file.iterrows():
    test_images(row)
