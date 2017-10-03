# Build brand SET manifest file zip (001)

import collections
import json
from operator import itemgetter
import zipfile
import os

cwd = os.getcwd()
from cwd + "/Brand_Manifest_Zip.py" import file_name, brands_file

# Build the hierarchy of brand ordinals
# Get each application in the file
# For each application, get the relevant locales
# For each locale in each application, get the relevant sets

# Distribute each brand and its proper ordinal to the corresponding set
# within the application/locale/set hierarchy
hierarchy = {}

for line in brands_file.iterrows():

    applications = line[1]["applications"].split(";")
    locales = line[1]["locales"].split(";")
    sets = str(line[1]["sets"]).split(";")
    ordinals = str(line[1]["ordinal"]).split(";")

    for app in applications:
        if app not in hierarchy:
            hierarchy[app] = {}

        for locale in locales:
            if locale not in hierarchy[app].keys():
                hierarchy[app][locale] = {}

            for brandset in sets:
                if brandset not in hierarchy[app][locale].keys():
                    hierarchy[app][locale][brandset] = [collections.OrderedDict(
                        [("name", line[1]["brand"]), ("ordinal", int(ordinals[sets.index(brandset)]))])]
                else:
                    hierarchy[app][locale][brandset].append(collections.OrderedDict(
                        [("name", line[1]["brand"]), ("ordinal", int(ordinals[sets.index(brandset)]))]))

for app in hierarchy.keys():
    for locale in hierarchy[app].keys():
        for brandset in hierarchy[app][locale].keys():
            # Build the manifest object for each set in each app/locale in the ref dictionary
            manifest = collections.OrderedDict([("setID", int(brandset)), ("application", app), ("locale", locale)])
            brand_ordinals = sorted(hierarchy[app][locale][brandset], key=itemgetter("ordinal"))
            manifest["brands"] = brand_ordinals

            set_manifest_filename = ".".join(["brandset.manifest", app, locale, brandset]) + ".json"

            with open(set_manifest_filename, "w") as fw:
                json.dump(manifest, fw)

            with zipfile.ZipFile(file_name + "-001.zip", "a") as brands_zip_1:
                brands_zip_1.write(set_manifest_filename, compress_type=zipfile.ZIP_DEFLATED)

            os.remove(set_manifest_filename)
