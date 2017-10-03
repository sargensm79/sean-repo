-- Spectrum data for Sainsbury's users

SET autocommit = 1;

SET @beginning = unix_timestamp('2017-09-16')*1000;

SET @ending = unix_timestamp('2017-10-01')*1000;

drop table if exists fkp;
create temporary table fkp (key (profileID)) as
SELECT DISTINCT
    userID AS foreignKey, profileID, creation
FROM
    reporting_viz.uxFunnel
        INNER JOIN
    foreignKeys ON foreignKeys.foreignKey = userID
WHERE
    uxFunnel.application = 'sainsburys.survey'
        AND stage = 'Completed Profile';


drop table if exists ps;
create temporary table ps (primary key (profileID))
SELECT 
    fkp.profileID, MAX(updateID) AS updateID
FROM
    fkp
        INNER JOIN
    profileSpectrums ON profileSpectrums.profileID = fkp.profileID
GROUP BY fkp.profileID;


drop table if exists pref;
create table pref (
	foreignKey varchar(128),
	profileID varchar(64),
	creation bigint(20),
	updateID bigint(20),
key (foreignKey, updateID));

INSERT INTO pref
SELECT 
    foreignKey, fkp.profileID, creation, updateID
FROM
    fkp
        INNER JOIN
    ps ON ps.profileID = fkp.profileID;


-- Get max spectrum update and min (spring campaign) creation time per fk
drop table if exists jpref;
create table jpref (
    foreignKey varchar(128),
    profileID varchar(64),
    updateID bigint(20),
    Creation varchar(64),
constraint pk primary key (foreignKey, updateID),
key (profileID, updateID));

INSERT INTO jpref
SELECT 
    fkm.foreignKey,
    profileID,
    fkm.updateID,
    fkm.Creation
FROM
    (SELECT 
        foreignKey,
            MAX(updateID) AS updateID,
            DATE_FORMAT(FROM_UNIXTIME(MIN(creation) / 1000), '%Y%m%d%H%i%s') AS Creation
    FROM
        pref
    GROUP BY foreignKey) AS fkm
        INNER JOIN
    pref ON pref.foreignKey = fkm.foreignKey
        AND pref.updateID = fkm.updateID;

drop table if exists pref;

-- Get spectrum data + foreign keys
SELECT
    foreignKey,
	jpref.profileID, 
    Creation,
    CONCAT(parentName, ':', name) AS name,
    value
FROM
    jpref
        INNER JOIN
    profileSpectrums ON profileSpectrums.profileID = jpref.profileID
        AND profileSpectrums.updateID = jpref.updateID