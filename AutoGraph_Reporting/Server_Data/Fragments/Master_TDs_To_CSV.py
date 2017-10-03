#############################   Pipe out the master tags demographics for 1+ applications to a readable CSV file from the SQL DB

import mysql.connector
import csv
import datetime
import os

home = os.path.expanduser("~")
os.chdir(home + "/desktop/")

today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")

cnx = mysql.connector.connect(user="root", password="ch33s3h4t31", host="173.194.111.19", database="reporting")
cur1 = cnx.cursor()

headers = ["Category", "Group", "Threshold", "isTagGroup", "Applications", "Locales", "Fragment", "Label",
           "Group Label", "Image URL"]
apps = []
badapps = []
print(
    "Enter applications you want included in the output file."
    "Enter \"done\" to produce file. Enter \"all\" for all applications.")

while True:
    application = input("Enter an application name: ")
    if application == "done":
        print(apps)
        break
    if application == "all":
        apps.extend(
            ["sainsburys.survey", "vodafoneuk", "regentst", "monitise.virginmoney", "syniverse.ezbankdemo", "metropcs",
             "autograph.marketing"])
        apps.sort()
        print(apps)
        break
    elif application not in apps:
        apps.append(str(application))
    else:
        print("Enter another application or check naming")
        continue

lst = []

for app in apps:
    cur1.callproc("td_master", [app])
    for row in cur1.stored_results():
        for item in row.fetchall():
            if item[0].startswith("Input problem"):
                print(item[0])
                badapps.append(item)
                continue
            else:
                lst.append(item)

appname = ""
if len(apps) > 1 and len(apps) < 5:
    appname = apps[0]
    for item in apps[1:]:
        if item not in badapps:
            appname = appname + "-" + item
        else:
            continue
elif len(apps) == 1:
    appname = apps[0]
elif len(apps) == 5:
    appname = "master"

with open("/users/seansargent/Desktop/tag-demographics-" + appname + "-" + today + ".csv", "w") as tdwrite:
    tdwriter = csv.writer(tdwrite)
    tdwriter.writerow(headers)
    for item in lst:
        tdwriter.writerow(item)
tdwrite.close()

print("File written!")

cur1.close()
cnx.close()
