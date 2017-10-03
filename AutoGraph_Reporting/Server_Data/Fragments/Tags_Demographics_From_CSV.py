# Package tag-demographics file into JSON zips for upload

import json
import csv
import zipfile
import os
import collections
import datetime
import io

today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
fpath = "/users/seansargent/Desktop/"


locales = []
fcat = []

input_file = "dataiq_tag_demographics.csv"
application = "autograph.dataiq"


# Get all locales and categories from the input file. Put into lists and sort.
with open(fpath+input_file, encoding="mac-roman") as catcher:
    catchappender = csv.reader(catcher)
    next(catchappender, None)
    for row in catchappender:
        if row[8].lower().strip() not in fcat:
            fcat.append(row[8].lower().strip())
        loca = row[5].split(";")
        for item in loca:
            if item not in locales:
                locales.append(item)
catcher.close()

locales.sort()
fcat.sort()


flist = []


# Group Labels File
llist = []


# grouplabels = collections.OrderedDict([("watch", "Watch")])
grouplabels = collections.OrderedDict([("shop", "Shop"), ("eat", "Eat"), ("play", "Play")])

for locale in locales:
    name = "grouplabels.manifest." + application + "-" + locale + ".json"
    fhand = open(name, "w")
    json.dump(collections.OrderedDict([("application", application),
                                       ("locale", locale), ("groups", grouplabels)]), fhand)
    fhand.close()
    llist.append(name)

labelZip = zipfile.ZipFile(fpath+"tag-demographics-"+application+"-"+today+"-001.zip", "w")

for file in llist:
    labelZip.write(file, compress_type=zipfile.ZIP_DEFLATED)
    os.remove(file)

labelZip.close()


# Package tag-demographics row into a dictionary object for appending to the list in the category JSON
def dictconstructing(row, category):
    return collections.OrderedDict([("category", row[0].split(":")), ("fragment", row[6]),
                                    ("label", row[7]), ("groupLabel", category), ("imageURL", row[9])])

# Write out the file containers...
# ...the application, specific locale, and specific category for this particular file (and empty descriptors list)
# Open csv file
# Starting with first nonblank line (where the group name equals the category and the locales match)
# Use the dictconstructing function to package row up
# Append row dict to empty descriptors list
# Write file to JSON, return file name
def fileconstructing(filename, category, locale):
    catdict = collections.OrderedDict([("application", application), ("locale", locale),
                                       ("name", category), ("isTagGroup", True), ("threshold", 1), ("descriptors", [])])
    with open(fpath+filename, encoding="mac-roman") as freader:
        fread = csv.reader(freader)
        for count, row in enumerate(fread):
            if count > 0 and row[8].lower() == category and locale in row[5].split(";"):
                if row[6] == "":
                    continue
                catdict["descriptors"].append((dictconstructing(row, row[8].lower())))
        freader.close()
    fname = "descriptorgroup.manifest."+application+"-"+locale+"-"+category+".json"
    # Write files out (in the current directory), return file names for easy access in a list
    fwrite = io.open(fname, "w", encoding="utf8")
    json.dump(catdict, fwrite, ensure_ascii=False)
    fwrite.close()
    return fname


for locale in locales:
    for category in fcat:
        # Write out JSON files for each category, append file names to list
        flist.append(fileconstructing(input_file, category, locale))


myzip = zipfile.ZipFile(fpath+"tag-demographics-"+application+"-"+today+"-000.zip", "w")

for file in flist:
    myzip.write(file, compress_type=zipfile.ZIP_DEFLATED)
    os.remove(file)
myzip.close()
