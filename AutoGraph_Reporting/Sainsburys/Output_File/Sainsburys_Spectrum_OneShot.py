import pandas as pd
import mysql.connector
import datetime
import time
import os

today = str(datetime.date.today()).replace("-", "")


def openfile(filename):
    fhand = open(filename)
    inp = fhand.read().split(";")
    fhand.close()
    return inp


sql_path = os.getcwd() + "/sql/one_shot/"

start = datetime.datetime.now()

cnx = mysql.connector.connect(user="root", password="ch33s3h4t31", host="104.199.98.18", database="reporting")

cursor1 = cnx.cursor()

for command in openfile(sql_path + "Spectrum.sql"):
    print(command)
    cursor1.execute(command)

spectrum = cursor1.fetchall()

print("Spectrum retrieved!")

df = pd.DataFrame(spectrum)

print("Pivoting")

pt = pd.pivot_table(df, index=[0, 1, 2], columns=3, values=4)

pt.reset_index(inplace=True)

cursor1.close()

time.sleep(15)

# Hard-coding time. Lazy programming for the win!
# This is designed to remove extraneous tag columns from old profiles sneaking into the dataset

# demographics/interests
dems = [col for col in pt.columns.tolist()[3:] if not col.startswith("tags")]

# restricted tag set
tags = open("cols.csv").read().split(",")

# new df with correct columns
pt = pt[[0,1,2] + dems + tags]

#####   CAMPAIGN VOTES

cursor2 = cnx.cursor()

print("Getting campaign votes...")

for command in openfile(sql_path + "Campaign_Votes.sql"):
    print(command)
    cursor2.execute(command)

cv = pd.DataFrame(cursor2.fetchall())

cvpt = pd.pivot_table(cv, index=[0], columns=1, values=2)

cvpt.reset_index(inplace=True)

cursor2.close()

time.sleep(15)


#####   BRAND VOTES

cursor3 = cnx.cursor()

print("Getting brand votes...")

for command in openfile(sql_path + "Brand_Votes.sql"):
    print(command)
    cursor3.execute(command)

dlbv = pd.DataFrame(cursor3.fetchall())

bvpt = pd.pivot_table(dlbv, index=[0], columns=1, values=2)

bvpt.reset_index(inplace=True)

cursor3.close()

time.sleep(15)


#####   DROP EXTRA TABLE

drop_cursor = cnx.cursor()

drop_cursor.execute("""DROP TABLE IF EXISTS jpref;""")

drop_cursor.close()

cnx.close()


#####   JOIN, WRITE DATAFRAMES

print("Joining dataframes...")

res = pd.merge(pd.merge(pt, bvpt, left_on=[0], right_on=[0], how="left"),
               cvpt, left_on=[0], right_on=[0], how="left")

res.rename(columns={0: "Foreign Key", 1: "autoGraph ID", 2: "Creation"}, inplace=True)

print("Writing to file...")

res.to_csv("sainsburys_spring_spectrum_" + today + ".csv", index=False)

print("Sainsburys file written!")

print(datetime.datetime.now() - start)
