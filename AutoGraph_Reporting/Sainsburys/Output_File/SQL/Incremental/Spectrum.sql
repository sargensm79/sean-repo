-- Sainsburys incremental spectrum

set @report_beginning = unix_timestamp('2017-05-20')*1000;

set @report_ending = unix_timestamp('2017-05-20')*1000;


-- Recent spectrum updates
drop table if exists ips;
create table ips (primary key (profileID)) as
SELECT 
    profileID, MAX(updateID) AS updateID
FROM
    profileSpectrums
WHERE
    updateID BETWEEN @report_beginning AND @report_ending
GROUP BY profileID;

-- Foreign keys
drop table if exists ifk;
create table ifk (key (foreignKey, updateID)) as
SELECT 
    foreignKey, ips.profileID, updateID, creation
FROM
    ips
        INNER JOIN
    foreignKeys ON application = 'sainsburys.survey'
        AND foreignKeys.profileID = ips.profileID;


-- Max profile/update/creation per fk
drop table if exists ifkf;
create table ifkf (constraint pk primary key (profileID, updateID)) as
SELECT 
    ifk.foreignKey, profileID, ifk.updateID, fkr.Creation
FROM
    ifk
        INNER JOIN
    (SELECT 
        foreignKey,
            MAX(updateID) AS updateID,
            DATE_FORMAT(FROM_UNIXTIME(MIN(creation) / 1000), '%Y%m%d%h%i%s') AS Creation
    FROM
        ifk
    GROUP BY foreignKey) AS fkr ON fkr.foreignKey = ifk.foreignKey
        AND fkr.updateID = ifk.updateID;


-- Drop legacy tables (except for previous one)
drop table if exists ips;
drop table if exists ifk;

-- Retrieve spectrum info
SELECT
    foreignKey,
	ifkf.profileID, 
    Creation,
    CONCAT(parentName, ':', name) AS name,
    value
FROM
    ifkf
        INNER JOIN
    profileSpectrums ON profileSpectrums.profileID = ifkf.profileID
        AND profileSpectrums.updateID = ifkf.updateID;