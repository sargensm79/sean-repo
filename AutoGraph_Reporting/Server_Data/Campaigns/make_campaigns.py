# Making offer tiles

import json
import zipfile
import hashlib
import base64
import csv
import os
import time
from bs4 import *

def urlSafeBase64String(unsafeString):
    unsafeBase64Characters = ["+", "=", "/"]
    safeBase64Characters = ["-", "~", "$"]
    escaped = ""
    for character in unsafeString:
        if character in unsafeBase64Characters:
            character = safeBase64Characters[unsafeBase64Characters.index(character)]
            escaped = escaped + character
        else:
            escaped = escaped + character
    return escaped

# Package assets into template
# If URL exists, follow it
# If no URL and the button indicates the offer
# is a context, change the CSS
# If no URL and offer is not a contest, no link/button

image_root = "https://storage.googleapis.com/autograph-public/threeuk/offers/images/"

def templating(template_file, csvline):

    template = open(template_file)

    soup = BeautifulSoup(template, "lxml")

    # Add image container
    img_container = soup.new_tag("img", src=image_root+csvline["Medium_image"]+".png", alt="Image")
    img_container["class"] = "header-container"

    soup.head.insert_after(img_container)

    # Get body-container div
    bc = soup.find("div", class_="body-container")

    # Add title
    new_title = soup.new_tag("div")
    new_title["class"] = "title"
    new_title.string = csvline["Title"]

    bc.insert(0, new_title)

    # Add description
    new_desc = soup.new_tag("div")
    new_desc["class"] = "desc"
    new_desc_text = soup.new_tag("p")
    new_desc_text.string = csvline["Description"]
    new_desc.append(new_desc_text)

    bc.insert(3, new_desc)

    # Add button to body if necessary
    if csvline["URL"] != "":
        new_link = soup.new_tag("a", href=csvline["URL"], target="_new")
        new_link["class"] = "button"
        new_link.string = csvline["Button text"]

        bc.insert(4, new_link)

    return soup.prettify()


def makeCampaignID(publisher, name):
    publisher = publisher.lower().encode(encoding='UTF-8')
    pID = hashlib.sha256()
    pID.update(publisher)
    publisherI = pID.digest()
    publisherID = urlSafeBase64String(base64.b64encode(publisherI).decode()).encode(encoding="UTF-8")

    name = name.lower().encode(encoding='UTF-8')
    cID = hashlib.sha256()
    cID.update(publisherID + name)
    campID = cID.digest()
    campaignID = urlSafeBase64String(base64.b64encode(campID).decode())
    return campaignID

# Set expiration timestamp (epoch, in ms)
raw_exp = time.mktime(time.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
expiration = int(raw_exp*1000)

def campaignCreation(csvLine):
    template = {}
    template["id"] = str(round(time.time()*1000))
    template["application"] = "threeuk"
    template["locales"] = ["en-uk", "en-us"]
    template["expiresActual"] = expiration
    template["activate"] = False
    template["setPinned"] = False
    template["publisher"] = csvLine["Publisher Feed Name"]
    template["title"] = csvLine["Title"]
    template["description"] = templating(os.getcwd() + "/templates/3_template.html", csvLine)

    template["images"] = dict([("large", dict([("size", "large"), ("url", image_root + csvLine["Large_image"] + ".png")])),
                                    ("medium", dict([("size", "medium"), ("url", image_root + csvLine["Medium_image"] + ".png")])),
                                    ("small", dict([("size", "small"), ("url", image_root + csvLine["Small_image"] + ".png")]))])
    
    template["markets"] = dict([("0", dict(
        [("display", "[location, gb]"), ("locality", None), ("country", "gb"), ("postalCode", "national"),
         ("latitude", None), ("longitude", None), ("approximate", True), ("maxTransport", 10)])), ("1", dict(
        [("display", "[location, us]"), ("locality", None), ("country", "us"), ("postalCode", "national"),
         ("latitude", None), ("longitude", None), ("approximate", True), ("maxTransport", 10)]))])
    
    template["timeWeight"] = 0.0
    template["ratingWeight"] = 1.0

    template["url"] = csvLine["URL"]
    template["tags"] = []
    for tag in csvLine["tags"].split(";"):
        template["tags"].append(dict([("name", tag), ("weight", 1.0)]))
    
    # Differentiate between collections/grouped offers
    if csvLine["Collection Title (if applicable)"].lower() == "collection tile":
        template["assets"] = [dict([("name", "groupTarget"), ("type", "text/plain"), ("disposition", "display"), ("text", csvLine["Title"].lower().replace(" ", ""))]),
                            dict([("name", "groupLabel"), ("type", "text/plain"), ("disposition", "display"), ("text", csvLine["Title"])])]
        template["displayGroups"] = ["."]
        template["setPinned"] == True
    elif csvLine["Collection Title (if applicable)"] == "NA":
        template["displayGroups"] = ["."]
    else:
        template["displayGroups"] = csvLine["Collection Title (if applicable)"].lower().replace(" ", "")

    # template["filters"] = [dict([("category", ["scales", csvLine[3]]), ("operator", ">="), ("value", 1.0)])]
    
    return template

campaign_file = input("Enter campaign CSV file name: ")

file_list = []

with open(os.getcwd + "/offer_csvs/" + campaign_file) as cr:
    creader = csv.DictReader(cr)
    for line in creader:
        campaign = campaignCreation(line)
        campaignID = urlSafeBase64String(makeCampaignID(campaign["publisher"], campaign["id"]))
        filename = "campaign.manifest." + campaignID + ".json"
        fwrite = open(filename, "w")
        json.dump(campaign, fwrite)
        fwrite.close()
        file_list.append(filename)
        time.sleep(1)

campaign_zip = zipfile.ZipFile("offers.zip", "w")

for file in file_list:
    try:
        campaign_zip.write(file, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(file)
    except:
        print("No File: ", file)

campaign_zip.close()