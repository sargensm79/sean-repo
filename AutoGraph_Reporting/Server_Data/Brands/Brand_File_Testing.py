import os
from PIL import Image
import pandas as pd
import requests

file_path = "/users/seansargent/Desktop/"

brands_file = "threeuk-brands-20171003.csv"

# Read brands file into a dataframe, work with different columns in memory
brands_dataframe = pd.read_csv(file_path+brands_file)

# Test column order/notation
target_headers = ['brand', 'ordinal', 'sets', 'icon', 'url', 'applications', 'locales']

file_headers = brands_dataframe.columns.tolist()

# Correct header spelling/order
print("Checking column order/spelling...")

if target_headers != file_headers[:7]:
    print("Error in the column names/orders")
    exit()
else:
    print("Column order/spelling correct")


# Correct column notation
print("Checking column notation...")

for header in file_headers[7:]:
    notation_length = len(header.split(":"))
    if notation_length < 2:
        print("Failed: field header '" + header + "' needs ':' notation")
        exit()

print("Column notations correct")

"""
print("Checking tag values")

# Check tag values - fail if not between 0-2000

tag_df = brands_dataframe[["brand"] + [column for column in brands_dataframe.columns if column.startswith("tags")]].set_index("brand")

tag_df.fillna(value=0, inplace=True)

for count, brand in enumerate(tag_df.iterrows()):
    # if brand[1].dtype != np.int64:
        # print("Error! Column is incorrectly typed - should be int64")
        # exit()
    if (brand[1] > 2000).any() | (brand[1] < 0).any():
        print("Error, tag values out of range at " + brand[0])
        exit()

print("Tag values in correct range")
"""
# Check image sizes (need to be 216x216)
print("Checking image sizes...")

brand_images = os.listdir(file_path+"brand-images/")

for image in brand_images:
    im = Image.open(file_path+"brand-images/"+image)
    if im.size != (216, 216):
        print(image, im.size)
        exit()

print("Image sizes correct")

print("Checking image names...")

# Check that all brand icon names are in the image folder
for icon in brands_dataframe["icon"]:
    if icon not in brand_images:
        print("'" + icon + "' missing from images folder")
        exit()
print("Image names correct")

print("Checking image URLs")

for iurl in brands_dataframe["url"]:
    r = requests.get(iurl)
    if r.status_code != 200:
            print(iurl)
            exit()

print("Image URLs correct")

# Build dict: keys are the set numbers, values are their ordinals (in list form)
sets = {}

for line in brands_dataframe[["brand", "ordinal", "sets"]].iterrows():
    co = line[1]["ordinal"].split(";")     # ordinal numbers
    cs = line[1]["sets"].split(";")     # set numbers
    # co = [line[1]["ordinal"]]     # UNCOMMENT FOR SINGLE-SET SORTER FILE
    # cs = [line[1]["sets"]]

    for setnumber in cs:
        # if setnumber == "2":

        # Ugly IF block here, sorry...
        # The gist: if a set number hasn't been recorded, add it and its corresponding ordinals to the dict
        # If it HAS been recorded already, append the ordinals to its existing list in the dict
        # The "append" allows duplicate ordinals to be added to the list for each set
        # These duplicates will be flagged in the next steps
            
        set_ordinal = co[cs.index(setnumber)]
            
            # print(line[1]["brand"], setnumber, set_ordinal)
            
        if setnumber not in sets:
            sets[setnumber] = [int(set_ordinal)]
        else:
            sets[setnumber].append(int(set_ordinal))

# Find missing ordinal values
def missing_ordinals(ordinal_list):

    # Create full list of ints between beginning and end of ordinal list
    full_set = set(range(1, max(ordinal_list) + 1))

    # Return ints in the full list that are not in the passed ordinal list
    return [str(ordin) for ordin in sorted(full_set-set(ordinal_list))]


for key, value in sets.items():
    print(key, sorted(value))

    # Build list of dupe ordinals
    dupe_ordinals = [str(ordinal) for ordinal in set(value) if value.count(ordinal) > 1]

    # Print out set number, duplicated ordinals, missing ordinals
    if not missing_ordinals(value) and not dupe_ordinals:
        continue
    else:
        print("Set: " + str(key))
        print("Duplicated Ordinal(s): " + ", ".join(dupe_ordinals))
        print("Missing Ordinal(s): " + ", ".join(missing_ordinals(value)))

dv = "Testing finished!"
