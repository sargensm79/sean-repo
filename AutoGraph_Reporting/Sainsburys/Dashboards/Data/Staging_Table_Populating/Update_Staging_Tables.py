# Get the current e-mail numbers
# Get the most recent numbers for the other stages
# Use it to update the dropoff and funnel tables

import pandas as pd
import sqlalchemy

cnx = sqlalchemy.create_engine("mysql+mysqlconnector://root:ch33s3h4t31@104.199.98.18:3306/reporting_viz")

print("Calculating stage counts...")

# Get the number of users in each stage by day
sql = """SELECT 
    Date,
    IF(stage = 'Completed Profile',
        'Completed Brand Votes',
        stage) AS stage,
    CASE
        WHEN stage = 'Landed on Page' THEN 1
        WHEN stage = 'Clicked to Start' THEN 2
        WHEN stage = 'Completed Profile' THEN 3
        WHEN stage = 'Viewed Food Panel' THEN 4
        WHEN stage = 'Viewed Activities Panel' THEN 5
        WHEN stage = 'Viewed Living Well Persona' THEN 6
        WHEN stage = 'Clicked ''Done''' THEN 7
    END AS stage_number,
    'sainsburys.survey' AS application,
    COUNT(ids.userID) AS count
FROM
    uxFunnel
        INNER JOIN
    ids ON ids.userID = uxFunnel.userID
WHERE
    ids.application = 'sainsburys.survey'
        AND stage != 'Viewed Recipe'
GROUP BY Date , stage , stage_number , application 
UNION SELECT 
    Date, stage, 0 AS stage_number, application, count
FROM
    chartStaging
WHERE
    stage = 'E-mail Sent'
        AND application = 'sainsburys.survey'
ORDER BY date , stage_number;"""

dff = pd.read_sql(sql, cnx)


# Explicitly create this object as a new pandas DF so the IDE won't get confused about its type
dff["Date"] = pd.to_datetime(dff["Date"])

# Simulate a left join - make sure there is something for every stage at every date
# No users reaching a given stage in a given hour would omit it from the DF and fuck everything up
# Replace nulls with 0
stages = [["Landed on Page", 1, "sainsburys.survey"], 
            ["Clicked to Start", 2, "sainsburys.survey"],
            ["Completed Brand Votes", 3, "sainsburys.survey"],
            ["Viewed Food Panel", 4, "sainsburys.survey"], 
            ["Viewed Activities Panel", 5, "sainsburys.survey"],
            [ "Viewed Living Well Persona", 6, "sainsburys.survey"],
            ["Clicked 'Done'", 7, "sainsburys.survey"]]

ds_ref = []

for date in set(dff["Date"]):
    for stage in stages:
        ds_ref.append([date] + stage)
        
stages = pd.DataFrame(ds_ref, columns = ["Date", "stage", "stage_number", "application"])

dff = pd.merge(stages, dff, how = "left", left_on = ["Date", "stage", "stage_number", "application"], 
    right_on = ["Date", "stage", "stage_number", "application"])

dff.fillna(0, inplace = True)

# Sort according to date and the "stage number", then delete the unnecessary stage number field
dff.sort_values(["Date", "stage_number"], ascending=True, inplace=True)


# Replace chartStaging table contents
del dff["stage_number"]
dff.to_sql("chartStaging", cnx, schema = "reporting_viz", if_exists = "replace", index = False)

print("Calculating dropoff...")

# Find the differences between a given stage and the next stage in the UX for each date
# Put in a dataframe. Every stage will be correct except for "Entered Contest", which has no "next stage"
usf = dff.set_index(["Date", "stage", "application"]).diff(-1)

# Get the original "Entered Contest" counts by date
contests = dff[dff["stage"] == "Clicked 'Done'"]

contests.set_index(["Date", "stage", "application"], inplace=True)

# Overwrite incorrect "Entered Contest" values in "difference" dataframe
usf.update(contests, overwrite=True)

usf.reset_index(inplace=True)

usf.to_sql("dropoff", cnx, schema = "reporting_viz", if_exists = "replace", index = False)

"""
print("Calculating profiles completed...")

pc = ""SELECT 
    Date, stage, 'sainsburys.survey' as application, COUNT(ids.userID) AS count
FROM
    uxFunnel
        INNER JOIN
    ids ON ids.userID = uxFunnel.userID
WHERE
    stage = 'Completed Profile'
GROUP BY Date , stage
ORDER BY Date;""

profiles_completed = pd.read_sql(pc, cnx)

profiles_completed.to_sql("chartStaging", cnx, schema = "reporting_viz", if_exists = "append", index = False)

print("Done, check tables for accuracy")
"""
