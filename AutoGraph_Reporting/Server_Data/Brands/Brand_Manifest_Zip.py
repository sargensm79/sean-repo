# Build brand file zip (000)

import hashlib
import base64
import pandas as pd
import collections
import json
import os
import shutil
import zipfile

cwd = os.getcwd()
from cwd + "/Brand_File_Testing.py" import dv

print(dv)


file_name = "autographmedia-brands-20140827"
image_folder = "images/"
image_path = cwd + "/" + image_folder


# Escape scary characters
def urlsafebase64string(unsafestring):
    unsafebase64characters = ["+", "=", "/"]
    safebase64characters = ["-", "~", "$"]
    escaped = ""
    for character in unsafestring:
        if character in unsafebase64characters:
            character = safebase64characters[unsafebase64characters.index(character)]
            escaped = escaped + character
        else:
            escaped = escaped + character
    return escaped


# Make hashed IDs (brand IDs or content IDs)
# Don't encode to UTF8 in non-string instances (i.e. image bytes)
def makebrandid(name):
    try:
        name = name.lower().encode(encoding='UTF-8')
    except:
        pass
    bid = hashlib.sha256()
    bid.update(name)
    brid = bid.digest()
    brandid = urlsafebase64string(base64.b64encode(brid).decode())
    return brandid


brands_file = pd.read_csv(file_name + ".csv")
brands_file["sets"] = 0

# Revise column order. Fucking old applications...
file_headers = brands_file.columns.tolist()

target_headers = ['brand', 'ordinal', 'sets', 'icon', 'applications', 'locales']

spec = file_headers[5:-1]

brands_file = brands_file[target_headers + spec]


# Build and zip the requisite files from the CSV + the image folders
def brandwriting(brand_dataframe):
    # Ordered object
    brand_dict = collections.OrderedDict()

    # Add native brand info (name, app, etc)
    brand_dict["name"] = brand_dataframe[1]["brand"]

    brand_dict["ordinal"] = [int(ordinal) for ordinal in str(brand_dataframe[1]["ordinal"]).split(":")]
    if len(brand_dict["ordinal"]) == 1:
        brand_dict["ordinal"] = brand_dict["ordinal"][0]

    brand_dict["sets"] = [int(brandset) for brandset in str(brand_dataframe[1]["sets"]).split(":")]
    if len(brand_dict["sets"]) == 1:
        brand_dict["sets"] = brand_dict["sets"][0]

    brand_dict["locales"] = brand_dataframe[1]["locales"].split(":")
    brand_dict["applications"] = brand_dataframe[1]["applications"].split(":")

    # Add spectrum
    brand_dict["category"] = []

    for item in spec:
        value = brand_dataframe[1][item]
        if pd.isnull(value):
            pass
        else:
            brand_dict["category"].append(
                collections.OrderedDict([("category", item.split(":")), ("value", int(brand_dataframe[1][item]))]))

    # Add images
    brand_dict["images"] = [collections.OrderedDict()]

    icon_name = brand_dataframe[1]["icon"]

    brand_dict["images"][0]["name"] = "icon"
    brand_dict["images"][0]["path"] = image_folder + icon_name
    brand_dict["images"][0]["contentName"] = "icon"

    with open(image_path + icon_name, "rb") as ir:
        image_bytes = ir.read()

    brand_dict["images"][0]["contentID"] = makebrandid(image_bytes)

    # Write out manifest/image files
    brandid = makebrandid(brand_dataframe[1]["brand"])

    shutil.copyfile(image_path + icon_name, "brand.image." + brandid + ".icon.png")

    fname = "brand.manifest." + brandid + ".json"
    with open(fname, "w") as fopen:
        json.dump(brand_dict, fopen,)

    with zipfile.ZipFile(file_name + "-000.zip", "a") as brands_zip_0:
        brands_zip_0.write(fname, compress_type=zipfile.ZIP_DEFLATED)
        brands_zip_0.write("brand.image." + brandid + ".icon.png", compress_type=zipfile.ZIP_DEFLATED)

    # Write the file out first, add it to zip, remove the original.
    # There has to be a better way to do this, right?
    os.remove(fname)
    os.remove("brand.image." + brandid + ".icon.png")

for line in brands_file.iterrows():
    brandwriting(line)