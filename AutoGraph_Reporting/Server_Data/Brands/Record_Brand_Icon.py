# Put image files in DB

import pandas as pd
import os
import sqlalchemy
import time

os.chdir("/users/seansargent/desktop/")

# Read csv with 2 fields: brand IDs and icon names
# Set image dimensions (maybe require this as input later)
df = pd.read_csv("brand_images.csv")        # Brand image CSV name goes here
imageSize = "216x216"

# Add required fields for DB fields
# Image dimensions, unix timestamp of addition to DB, image URL
df["imageSize"] = imageSize
df["last_update"] = round(time.time()*1000)

df["image_root"] = "https://storage.googleapis.com/autograph-public/brand-images/" + imageSize + "/"
df["imageURL"] = df["image_root"] + df["icon"]

# Only the correct columns
# Deprecate this once we're not just using the brands files for the inserts...
df = df[["BRAND_ID", "imageSize", "imageURL", "last_update"]]

cnx = sqlalchemy.create_engine(
    "mysql+mysqlconnector://root:ch33s3h4t31@autograph-data-cluster-1.cluster-cxsfh4siyclv.us-west-2.rds.amazonaws.com:3306/data_science")

df.to_sql(name="brandImages", con=cnx, schema="data_science", if_exists="append", chunksize=5000, index=False)
