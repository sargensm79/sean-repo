-- Add profiles created to IDs ref table and to uxFunnel table

CREATE DEFINER=`root`@`%` PROCEDURE `profiles_created`(IN app VARCHAR(32))
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 

    ROLLBACK;

    insert into reporting_viz.procedureErrors (
    select now(), 'profiles_created', app
    );

START TRANSACTION;

-- Establish newly created IDs

set @prev_date = date_add(curdate(), interval -1 day);

set @prev_date_start = unix_timestamp(@prev_date)*1000;

set @prev_date_end = unix_timestamp(curdate())*1000;

set @prev_cd = date_format(@prev_date, '%Y%m%d');


-- FK apps

IF app in('sainsburys.survey', 'directline')

THEN

-- Created FKs first
drop table if exists new_fks;
create temporary table new_fks (primary key (foreignKey)) as
SELECT 
    fkc.foreignKey, MIN(foreignKeys.cohortDay) AS cohortDay
FROM
    (SELECT DISTINCT
        foreignKey
    FROM
        foreignKeys
    WHERE
        application = app
            AND cohortDay = @prev_cd
            AND foreignKey != '') AS fkc
        INNER JOIN
    foreignKeys ON foreignKeys.foreignKey = fkc.foreignKey
WHERE
    application = app
        AND cohortDay > '20170915'	-- Project start date
GROUP BY fkc.foreignKey
HAVING cohortDay = @prev_cd;


-- Creation date (fks)
insert ignore into reporting_viz.ids
(SELECT 
    foreignKey, @prev_date, app
FROM
    (SELECT 
        new_fks.foreignKey, ids.userID
    FROM
        new_fks
    LEFT JOIN reporting_viz.ids ON ids.userID = new_fks.foreignKey
        AND application = app) AS existing_test
WHERE
    userID IS NULL);



-- Went to brands stage
insert ignore into reporting_viz.uxFunnel
SELECT DISTINCT
    foreignKey, 'Viewed Brand Sorter' AS stage, app
FROM
    (SELECT DISTINCT
        profileID
    FROM
        profileEvents
    WHERE
        application = app
            AND eventType = 'buttonClicked'
            AND creation BETWEEN @prev_date_start AND @prev_date_end
            AND eventValue = 'goToBrands') AS go_to_brands
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = go_to_brands.profileID
        INNER JOIN
    reporting_viz.ids ON ids.userID = foreignKeys.foreignKey
WHERE
    foreignKey != '';


ELSEIF app = 'regentst'

THEN

-- Created agIDs first
drop table if exists new_profiles;
create temporary table new_profiles (primary key (profileID)) as
SELECT DISTINCT
    profileID, cohortDay
FROM
    profiles
WHERE
    application = app
        AND cohortDay = @prev_cd;


-- Creation date (agID)
insert ignore into reporting_viz.ids
(SELECT 
    profileID, @prev_date, app
FROM
    (SELECT 
        new_profiles.profileID, ids.userID
    FROM
        new_profiles
    LEFT JOIN reporting_viz.ids ON ids.userID = new_profiles.profileID
        AND application = app) AS existing_test
WHERE
    userID IS NULL);


-- Went to brands stage (agID)
insert ignore into reporting_viz.uxFunnel
(SELECT DISTINCT
    profileID, 'Viewed Brand Sorter', app
FROM
    profileEvents
WHERE
    application = app
        AND eventType = 'buttonClicked'
        AND creation BETWEEN @prev_date_start AND @prev_date_end
        AND eventValue = 'goToBrands');

ELSE

SELECT 'unknown app, revise procedure';


END IF;

-- Created stage (all)
insert ignore into reporting_viz.uxFunnel
(SELECT 
    userID, 'Created Profile', app
FROM
    reporting_viz.ids
WHERE
    Date = @prev_date AND application = app);


COMMIT;


END