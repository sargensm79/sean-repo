# Produce the spectrum extract for the past 2 hours
print "Running spectrum extract..."

import time
import MySQLdb
import pandas as pd
import datetime

# Read all commands in a SQL file
def openfile(filename):
    fhand = open(filename)
    inp = fhand.read().split(";")
    fhand.close()
    return inp

# Execute SQL commands, return result set
# Exit program if no data (since there won't be a file to write)
def getsqldata(filepath):
    cur1 = cnx.cursor()
    for command in openfile(filepath):
        try:
            cur1.execute(command)
        except:
            print command
            exit()
            
    result_data = list(cur1.fetchall())
    time.sleep(10)
    cur1.close()
    
    if not result_data:
        print "No data for " + filepath + " in specified time range"
        exit()
    else:
        return result_data

# Optional function - give QA the option to set their own time limit
# IF YOU CHOOSE TO CALL THIS, comment out line 6 of "/home/ubuntu/Spectrum/Spectrum.sql"
def setTime(connection):
    time_component = raw_input("Enter time component (hour | day | month): ")
    
    if time_component not in ["hour", "month", "day"]:
        print """What? '""" + time_component + """' wasn't an allowed date type. 
And I'm too lazy to write an infinite loop to help you, so try again."""
        exit()
    
    time_length = raw_input("Enter time length (int): ")
    try:
        tl = int(time_length)
    except:
        print """What? '""" + time_length + """' wasn't an integer. 
And I'm too lazy to write an infinite loop to help you, so try again."""
        exit()

    var_cursor = connection.cursor()
    var_cursor.execute("""select date_format(date_add(now(), interval -""" + time_length + " " + time_component + """),
            '%Y-%m-%d %H:00:00') into @start_time;""")
    var_cursor.close()



sql_path = "/home/ubuntu/Spectrum/SQL/"

cnx = MySQLdb.connect(user="root", passwd="ch33s3h4t31", host="104.154.157.224", db="reporting")

# setTime(cnx)

# Retrieve/pivot spectrum data
spectrum = pd.DataFrame(getsqldata(sql_path + "Spectrum.sql"),
                        columns=["Foreign Key", "autoGraph ID", "Created timestamp", "Last Update", "name", "value"])

spectrum = pd.pivot_table(spectrum, index=["Foreign Key", "autoGraph ID", "Created timestamp", "Last Update"],
                          columns="name", values="value")
spectrum.reset_index(inplace=True)


# Retrieve/pivot brand votes
brand_votes = pd.DataFrame(getsqldata(sql_path + "Brand_Votes.sql"),
                            columns=["Foreign Key", "name", "vote"])

brand_votes = pd.pivot_table(brand_votes, index="Foreign Key", columns="name",
                             values="vote")
brand_votes.reset_index(inplace=True)

cnx.close()


# Merge, write to file
res = pd.merge(spectrum, brand_votes, how="left", left_on="Foreign Key",
               right_on="Foreign Key")

filename = "threeuk-profile-spectrum-" + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S") + ".csv"

res.to_csv(filename, index=False)


# Build extract file name to spec for later use...

min_update = min(res["Last Update"])
prefix = (min_update[:10].replace("-", "") + "000000")

max_update = max(res["Last Update"])
suffix = max_update.replace("-", "").replace(" ", "").replace(":", "")

extract_name = "AutoGraph_Profile_Detail_" + prefix + "_" + suffix + ".csv"
