# Create new tag-demographics zip files for upload (using database procedure)

import mysql.connector
import datetime
import json
import collections
import zipfile
import os
import io

application = input("Enter application string: ")
locale = input("Enter foreign locale OR enter \'all\' for all English fragments: ")

if locale == "all":
    locale = None

today = datetime.datetime.strftime(datetime.date.today(), "%Y%m%d")
fpath = "/users/seansargent/Desktop/"

locales = []
fcat = []
rstore = []

cnx = mysql.connector.connect(user="root", password="ch33s3h4t31", host="173.194.111.19", database="reporting")
cur1 = cnx.cursor()

cur1.callproc("tags_demos", [application, locale])

# Store rows in list so you can close the cursor
# Strip whitespace from categories and locales
# Store unique categories and locales in respective lists. Sort the lists.
for item in cur1.stored_results():
    for record in item.fetchall():
        rstore.append(record)
        if record[8].lower().strip() not in fcat:
            fcat.append(record[8].lower().strip())
        loca = record[5].split(";")
        for l in loca:
            if l.strip() not in locales:
                locales.append(l.strip())
cur1.close()

locales.sort()
fcat.sort()

# For each locale, write out the ordered group label JSON
# Store each JSON in a single zip file and remove it from the OS afterwards
llist = []

grouplabels = collections.OrderedDict([("shop", "Shop"), ("eat", "Eat"), ("play", "Play")])

for taglocale in locales:
    name = "grouplabels.manifest." + application + "-" + taglocale + ".json"
    fhand = open(name, "w")
    json.dump(collections.OrderedDict([("application", application),
                                       ("locale", taglocale), ("groups", grouplabels)]), fhand)
    fhand.close()
    llist.append(name)

labelZip = zipfile.ZipFile(fpath + "tag-demographics-" + application + "-" + today + "-001.zip", "w")

for file in llist:
    labelZip.write(file, compress_type=zipfile.ZIP_DEFLATED)
    os.remove(file)

labelZip.close()


# Package tag-demographics row into a dictionary object for appending to the list in the category JSON
def dictconstructing(row, category):
    return collections.OrderedDict([("category", row[0].split(":")), ("fragment", row[6]),
                                    ("label", row[0].split(":")[1]), ("groupLabel", category), ("imageURL", row[9])])


# Write out the file containers...
# ...the application, specific locale, and specific category for this particular file (and empty descriptors list)
# Traverse row list
# (Where the group name equals the category and the locales match), use the dictconstructing function to package row up
# Append row dict to empty descriptors list
# Write file to JSON, return file name
def fileconstructing(category, locale):
    catdict = collections.OrderedDict([("application", application), ("locale", locale),
                                       ("name", category), ("isTagGroup", True), ("threshold", 1), ("descriptors", [])])
    for row in rstore:
        if row[8].lower() == category and locale in row[5].split(";"):
            catdict["descriptors"].append((dictconstructing(row, row[8].lower().strip())))
    fname = "descriptorgroup.manifest." + application + "-" + locale + "-" + category + ".json"
    # Write files out (in the current directory), return file names for easy access in a list
    fwrite = io.open(fname, "w", encoding="utf8")
    json.dump(catdict, fwrite, ensure_ascii=False)
    fwrite.close()
    return fname


flist = []

# Construct fragment descriptors for each category (per locale)
# Write out JSON files, store files in zip, then remove from OS
for region in locales:
    for group in fcat:
        # Write out JSON files for each category, append file names to list
        flist.append(fileconstructing(group, region))

myzip = zipfile.ZipFile(fpath + "tag-demographics-" + application + "-" + today + "-000.zip", "w")

for file in flist:
    myzip.write(file, compress_type=zipfile.ZIP_DEFLATED)
    os.remove(file)
myzip.close()
