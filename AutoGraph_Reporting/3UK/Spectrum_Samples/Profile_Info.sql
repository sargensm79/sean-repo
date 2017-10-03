# Profile info

# Get profile IDs (all) and creations for the FKs in the file
drop table if exists fkc;
create temporary table fkc (key (foreignKey, creation)) as
SELECT DISTINCT
    cfk.foreignKey, profileID, creation
FROM
    customer_fks cfk
        INNER JOIN
    foreignKeys ON foreignKeys.foreignKey = cfk.foreignKey;


# Get FK creation date and most recently created profile ID
drop table if exists fkc;
create temporary table fkp (primary key (profileID)) as
SELECT 
    fkr.foreignKey, created_date, profileID
FROM
    (SELECT 
        foreignKey,
            MIN(creation) AS created_date,
            MAX(creation) AS creation
    FROM
        fkc
    GROUP BY foreignKey) AS fkr
        INNER JOIN
    fkc ON fkc.foreignKey = fkr.foreignKey
        AND fkc.creation = fkr.creation;


# Get most recent spectrum update time for those profile IDs
drop table if exists fk_updates;
create table fk_updates(constraint pk primary key (profileID, updateID)) as
SELECT 
    foreignKey,
    fkp.profileID,
    created_date,
    MAX(updateID) AS updateID
FROM
    fkp
        LEFT JOIN
    profileSpectrums ON profileSpectrums.profileID = fkp.profileID
GROUP BY foreignKey , fkp.profileID , created_date;

drop table customer_fks;

# For any that haven't updated: check if a previous profile for that FK updated
# If not, leave updateID as null
# If so, update profile ID to be most recent spectrum complete profile ID (and update the updateID)
SELECT 
    COUNT(*)
FROM
    fk_updates
WHERE
    updateID IS NULL INTO @null_count;

CALL spec_profiles_only(@null_count);


# Format timestamps and select
SELECT 
    foreignKey AS AG_ID,
    DATE_FORMAT(FROM_UNIXTIME(created_date / 1000),
            '%Y-%m-%d %H:%i:%s') AS 'Created timestamp',
    DATE_FORMAT(FROM_UNIXTIME(IFNULL(updateID, created_date) / 1000),
            '%Y-%m-%d %H:%i:%s') AS 'Last Update'
FROM
    fk_updates;