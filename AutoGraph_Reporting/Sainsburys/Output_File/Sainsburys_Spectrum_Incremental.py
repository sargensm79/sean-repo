# Get spectrum information of all profiles that updated spectrum information, brand votes,
# or campaign votes in past day/week/whatever

import mysql.connector
import pandas as pd
import csv
import datetime
import os
import time

today = str(datetime.date.today()).replace("-", "")


def openfile(filename):
    fhand = open(filename)
    inp = fhand.read().split(";")
    fhand.close()
    return inp


sql_path = os.getcwd() + "/sql/incremental/"

# Reminder to learn regex...right after solving world hunger
old_file = [file for file in os.listdir() if file.startswith("sainsburys.survey")][0]

cnx = mysql.connector.connect(user="root", password="ch33s3h4t31", host="104.199.98.18", database="reporting")

### Get spectrum data

cursor1 = cnx.cursor()

master_rows = []

for command in openfile(sql_path + "Spectrum.sql"):
    print(command)
    cursor1.execute(command)

for count, line in enumerate(cursor1):
    print(count)
    master_rows.append(line)

print("Adding to dataframe")
spectrum_data = pd.DataFrame(master_rows, columns=["Foreign Key", "autoGraph ID", "Creation", "name", "value"])

del master_rows

print("Pivoting")
spectrum_data = pd.pivot_table(spectrum_data, index=("Foreign Key", "autoGraph ID"), columns="name", values="value")

spectrum_data.reset_index(inplace=True)

cursor1.close()

time.sleep(15)

### Get campaign votes

print("Getting campaign votes")
cursor2 = cnx.cursor()

for command in openfile(sql_path + "Campaign_Votes.sql"):
    print(command)
    cursor2.execute(command)

cv = []

for item in cursor2:
    cv.append(tuple([item[0]] + [item[1]] + [int(item[2])]))

cursor2.close()

print("Adding campaign votes to dataframe")
campaign_votes = pd.DataFrame(cv, columns=["Foreign Key", "Title", "Vote"])

del cv

print("Pivoting")
campaign_votes = pd.pivot_table(campaign_votes, index="Foreign Key", columns="Title", values="Vote")

campaign_votes.reset_index(inplace=True)

time.sleep(15)

### Get brand votes

print("Getting brand votes")
cursor3 = cnx.cursor()

for command in openfile(sql_path + "Brand_Votes.sql"):
    print(command)
    cursor3.execute(command)

bv = []

for item in cursor3:
    bv.append(tuple([item[0]] + [item[1]] + [int(item[2])]))

cursor3.close()

print("Adding brand votes to dataframe")
brand_votes = pd.DataFrame(bv, columns=["Foreign Key", "Brand", "Vote"])

del bv

print("Pivoting")
brand_votes = pd.pivot_table(brand_votes, index="Foreign Key", columns="Brand", values="Vote")

brand_votes.reset_index(inplace=True)

cursor3.close()

cnx.close()

time.sleep(15)

print("Joining dataframes")

res = pd.merge(pd.merge(spectrum_data, brand_votes, how="left", left_on="Foreign Key",
               right_on="Foreign Key"), campaign_votes, how="left", left_on="Foreign Key",
               right_on="Foreign Key")

headers = []

with open(old_file) as specreader:
    sr = csv.reader(specreader)
    for line in sr:
        for item in line:
            headers.append(item)
        break

header_ref = pd.DataFrame(columns=headers)

# Append to existing headers
new_spectrum = header_ref.append(res)

# Revise order of headers
new_spectrum = new_spectrum[headers]

new_spectrum.fillna(value="", inplace=True)


# Return a new row of FK data (formatted for use in DataFrames)
# Only applies when there is a match between the existing spectrum file and the "new" spectrum file ("new_spectrum" variable)
def lineSwap(line):
    nr = new_spectrum[new_spectrum["Foreign Key"] == line]
    for row in nr.iterrows():
        index, data = row
    return [str(item) for item in data.tolist()]


fks = new_spectrum["Foreign Key"].tolist()

print("writing file")

# Don't copy FKs with existing data if they exist in the "new spectrum" dataframe (i.e. were updated)
# Instead, write their new data
# Rewrite existing FKs that don't have new data
# Append entirely new FKs and their new data
with open("sainsburys.survey-profile-spectrum-" + today + ".csv", "w") as filewriter:
    fw = csv.writer(filewriter, lineterminator="\n")
    fw.writerow(headers)
    with open(old_file) as specreader2:
        sr2 = csv.reader(specreader2)
        next(sr2, None)
        for line in sr2:
            if line[0] in fks:
                fw.writerow(lineSwap(line[0]))
                fks.remove(line[0])
            else:
                fw.writerow(line)
        for fk in fks:
            fw.writerow(lineSwap(fk))

os.remove(old_file)
