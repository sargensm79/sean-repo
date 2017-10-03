##########      Take a NEW tags-demos file and pump it into the DB table

import mysql.connector
import time
import csv

current_timestamp = int(round(time.time() * 1000))

lst = []
applications = []
locales = []

fname = "tmt_tag_demographics.csv"


with open("/users/seansargent/Desktop/"+fname) as appfile:
    appreader = csv.reader(appfile)
    next(appreader, None)
    for row in appreader:
        for app in row[4].split(";"):
            if app not in applications:
                applications.append(app.strip())
        for loc in row[5].split(";"):
            if loc not in locales:
                locales.append(loc.strip())
appfile.close()

applications.sort()
locales.sort()

with open("/users/seansargent/Desktop/"+fname) as tdfile:
    tdreader = csv.reader(tdfile)
    next(tdreader, None)
    for row in tdreader:
        for locale in locales:
            for app in applications:
                if row[6] == "":
                    continue
                elif row[9] != "":
                    lst.append(tuple([str(row[7]), app,
                                      locale, current_timestamp, "imageURL", row[9].strip()]))             # Image URL
                    lst.append(tuple([str(row[7]), app,
                                      locale, current_timestamp, "groupName", row[8].lower().strip()]))    # Group label
                    lst.append(tuple([str(row[7]), app,
                                      locale, current_timestamp, "fragment", row[6].strip()]))             # Fragment
                else:
                    lst.append(tuple([str(row[7]), app,
                                      locale, current_timestamp, "groupName", row[8].lower().strip()]))
                    lst.append(tuple([str(row[7]), app,
                                      locale, current_timestamp, "fragment", row[6].strip()]))
tdfile.close()


cnx = mysql.connector.connect(user="root", password="ch33s3h4t31", host="173.194.111.19", database="reporting")
cur1 = cnx.cursor()

cur1.executemany("""INSERT INTO tagFragments (tag, application, locale, updateID, contentName, contentText) 
                    VALUES (%s, %s, %s, %s, %s, %s)""", lst)

cnx.commit()

cur1.close()

cnx.close()
