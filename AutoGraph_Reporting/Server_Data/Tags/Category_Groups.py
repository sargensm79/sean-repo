# Make category-groups file for server upload

import mysql.connector
import collections
import json
import operator
import zipfile
import datetime
import os

cnx = mysql.connector.connect(user="root", password="ch33s3h4t31", host="173.194.111.19", database="reporting")

cur1 = cnx.cursor()

# From the database - grab all tags and their associated categories (and parent categories if applicable)

cur1.execute("""select tagRef.tag, tagRef.tagCategory, parentCategories.parentCategory
from tagRef
left join parentCategories
on parentCategories.subCategory = tagRef.tagCategory
group by tagRef.tag;""")

# Store all rows in a list so you can close the cursor
# If the third column is NULL (i.e. the tag has only one parent category), jam the parent category in a dictionary and give it an empty list for its tags
# If the third column is NOT NULL (i.e. the tag's category is a subcategory), jam the tag's category in a separate dictionary and give it its own dictionary
# The subcategory's dictionary will enable storage of tags AND parent names (for joining later on)

ref = []                # Store the rows here
onelevel = {}           # Categories without children
twolevel = {}           # Categories with children

for row in cur1:
    ref.append(row)
    if row[2] is None:
        onelevel[row[1]] = []
    else:
        twolevel[row[1]] = {}

cur1.close()
cnx.close()

# Traverse the rows and the "one-category" dictionary keys
# If the tag in the row has only one category and the category matches the dictionary key, append the tag to the key's list
# Sort list alphabetically (case-insensitive)

for key in onelevel:
    for item in ref:
        if item[2] is None and item[1] == key:
            onelevel[key].append(item[0])
    onelevel[key].sort(key=lambda s:s.lower())

# Add empty list tp "two-level" nested dictionaries for tags
# Traverse the rows - if the tag has a parent AND subcategory, append it to the tags list
# Also jam in the parent category to the nested dictionary for reference late

for key in twolevel:
    twolevel[key]["tags"] = []

for key in twolevel:
    for item in ref:
        if item[2] is not None and item[1] == key:
            twolevel[key]["tags"].append(item[0])
            twolevel[key]["parent"] = item[2]
    twolevel[key]["tags"].sort(key=lambda s:s.lower())

# Traverse both one-category and two-category dictionaries for parent names
# Append all parent categories to separate list (no duplicates)

catfinal = []

for key in onelevel:
    if key not in catfinal:
        catfinal.append(key)

for key, value in twolevel.items():
    if value["parent"] not in catfinal:
        catfinal.append(value["parent"])


dictfinal = []
finalref = []

# Append all the categories without a subcategory to a new list (ugly, I know)
# Format all the one-level categories and their tags into an ordered dictionary and append to final list for file-writing

for cat in catfinal:
    for category, list in onelevel.items():
        for key, value in twolevel.items():
            if cat == category and cat != key:
                dictfinal.append(collections.OrderedDict([("category", category), ("tags", list), ("tagCategories", [])]))
                finalref.append(category)
                break

# If the categories DO have subcategories, format them into ordered dictionary and append them to the list of categories without subcategories (for master list)

for cat in catfinal:
    if cat not in finalref:
        dictfinal.append(collections.OrderedDict([("category", cat), ("tags", []), ("tagCategories", [])]))


# For the categories WITH subcategories in the master list
# Append the subcategory dictionaries
# Append the final nested dictionary to the list and sort it

for item in dictfinal:
    for key, value in twolevel.items():
        if value["parent"] == item["category"]:
            item["tagCategories"].append(collections.OrderedDict([("category", key), ("tags", value["tags"]), ("tagCategories", [])]))
            item["tagCategories"].sort(key=operator.itemgetter("category"))

dictfinal.sort(key=operator.itemgetter("category"))

# Write the dictionary to JSON and put the file names in the list for zipping

flist = []

def jsonWriting(dict):
    fname = "tagcategory.manifest."+dict["category"].lower() + ".json"
    with open(fname, "w") as jfile:
        json.dump(dict, jfile)
    jfile.close()
    return fname

for item in dictfinal:
    flist.append(jsonWriting(item))

today = datetime.datetime.strftime(datetime.date.today(), "%Y%m%d")

myzip = zipfile.ZipFile("category-groups-"+today+"-000.zip", "w")

for file in flist:
    myzip.write(file, compress_type=zipfile.ZIP_DEFLATED)
    os.remove(file)
myzip.close()