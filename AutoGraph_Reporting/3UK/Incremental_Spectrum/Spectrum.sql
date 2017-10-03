# 3UK spectrum / profile info crap

SET autocommit = 1;

# Get 2 hours ago
select date_format(date_add(now(), interval -20 day), '%Y-%m-%d %H:00:00') into @start_time;
select unix_timestamp(@start_time)*1000 into @start_timestamp;

# Get ending time frame
select date_add(date_format(now(), '%Y-%m-%d %H:00:00'), interval -1 second) into @end_time;
# select unix_timestamp(@end_time)*1000 into @end_timestamp;
select unix_timestamp(now())*1000 into @end_timestamp;

# Profiles and their most recent update times
create temporary table spec_updates (key (profileID)) as
SELECT 
    spec_updates.*
FROM
    (SELECT
        profileID, max(updateID) as updateID
    FROM
        profileSpectrums
    WHERE
        updateID BETWEEN @start_timestamp AND @end_timestamp
	group by profileID) AS spec_updates
        INNER JOIN
    profiles ON profiles.profileID = spec_updates.profileID
WHERE
    application = 'threeuk';

# Join to FKs to get overall creation time per FK
# Stupid GTID rules prevent CREATE TABLE AS (SELECT...)
# So separate CREATE and INSERT
create table spec_keys (
	foreignKey varchar(128),
	profileID varchar(64),
    updateID bigint,
    creation bigint,
	key (foreignKey, updateID));

INSERT INTO spec_keys
SELECT 
    foreignKey, su.profileID, updateID, creation
FROM
    spec_updates su
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = su.profileID;

# Get min creation time / max update time at FK level
# Join back to get that FK's profile ID at its max update time (needed to retrieve remaining spectrum information)
create table key_creation (
	foreignKey varchar(128),
    profileID varchar(64),
    creation bigint,
    updateID bigint,
key (profileID, updateID));

INSERT INTO key_creation
SELECT 
    sk.foreignKey, profileID, sk.creation, sk.updateID
FROM
    (SELECT 
        foreignKey,
            MIN(creation) AS creation,
            MAX(updateID) AS updateID
    FROM
        spec_keys
    GROUP BY foreignKey) AS sk
        INNER JOIN
    spec_keys ON spec_keys.foreignKey = sk.foreignKey
        AND spec_keys.updateID = sk.updateID;
    
    
DROP TABLE spec_keys;

# Retrieve spectrum data and profile info
# Pivot in pandas
SELECT 
    foreignKey AS 'Foreign Key',
    kc.profileID AS 'autoGraph ID',
    DATE_FORMAT(FROM_UNIXTIME(kc.creation / 1000),
            '%Y-%m-%d %H:%i:%S') AS 'Created timestamp',
    DATE_FORMAT(FROM_UNIXTIME(kc.updateID / 1000),
            '%Y-%m-%d %H:%i:%S') AS 'Last Update',
    CONCAT(parentName, ':', name) AS name,
    value
FROM
    key_creation kc
        INNER JOIN
    profileSpectrums ps ON ps.profileID = kc.profileID
        AND ps.updateID = kc.updateID
