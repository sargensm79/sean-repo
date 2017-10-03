# Read new brands file
# Rename column, rejigger locales and applications, fill in image names

import pandas as pd
import os
import sqlalchemy
import requests
import shutil
import datetime

applications = "threeuk"

os.chdir("/users/seansargent/desktop/")

df = pd.read_csv("irene_three_sorter_20170906.csv")

del df["UPDATE_DATE.x"]

# Save columns (use them later for reordering)
cols = df.columns.tolist()

df["applications"] = applications
df["locales"] = "en-uk;en-us"

# Shorter to drop the (empty) icon field and re-add it later
# Maybe just ask Irene in the future to either pre-fill it or stop returning it
del df["icon"]

# Read the 216x216 brand names, image links and icon names into a DF
# Join with the CSV on brand name
cnx = sqlalchemy.create_engine(
    "mysql+mysqlconnector://root:ch33s3h4t31@autograph-data-cluster-1.cluster-cxsfh4siyclv.us-west-2.rds.amazonaws.com:3306/data_science")

sql = """SELECT 
    BRAND_ID AS brand,
    imageURL,
    SUBSTRING_INDEX(imageURL, '/', - 1) AS icon
FROM
    brandImages
WHERE
    imageSize = '216x216';"""

icons = pd.read_sql_query(sql, con=cnx)

res = pd.merge(df, icons, how="left", left_on="brand", right_on="brand")

# Make new folder locally for images
# May not need this when Dave passes down the brands image URL spec from on high
newpath = os.getcwd() + "/brand-images"
if not os.path.exists(newpath):
    os.mkdir(newpath)


# Read image URL
# Save in new directory as icon_name.png
def image_save(iurl):
    image_filename = iurl.split("/")[-1]

    r = requests.get(iurl, stream=True)

    with open(newpath + "/" + image_filename, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


for imageurl in res["imageURL"]:
    if pd.isnull(imageurl):
        continue
    else:
        image_save(imageurl)

res.to_csv("3UK_WITH_IMAGE_URLS.csv", index=False)

# Reorder columns, write out
res = res[cols]
today = (str(datetime.date.today()))
res.to_csv(applications + "-brands-" + today + ".csv", index=False)
