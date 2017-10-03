######  Take a category-groups zip and pipe out a readable CSV

import zipfile, json, csv, itertools, os, datetime

file_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")

directory = os.listdir(folder_path)

data = ""

for item in directory:
    if "category-groups" in item:
        data = directory[(directory.index(item))]

headers = []
rows = []

fwrite = open("master-tag-list-" + file_date + ".csv", "w")

filewriter = csv.writer(fwrite)

filenames = []

try:
    oogle = zipfile.ZipFile(data, "r")
except:
    print("No category-groups file present - recheck directory")
    exit()

for name in oogle.namelist():
    #if "regent st. brands" in name:
     #   continue
    data = json.loads((oogle.read(name).decode("utf-8")))
    cat = data["category"]
    if data["tags"]:
        headers.append(cat)
        rows.append(data["tags"])
    if not data["tagCategories"]:
        continue
    else:
        for item in data["tagCategories"]:
            headers.append(cat+":"+item["category"])
            rows.append(item["tags"])
oogle.close()


filewriter.writerow(headers)

for item in itertools.zip_longest(*rows):
    filewriter.writerow(item)

fwrite.close()