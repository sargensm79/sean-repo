-- Update IDs with their completed stages of the UX

CREATE DEFINER=`root`@`%` PROCEDURE `funnel_completion`(IN app VARCHAR(32))
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 

    ROLLBACK;

    insert into reporting_viz.procedureErrors (
    select now(), 'funnel_completion', app
    );

START TRANSACTION;

# Campaigns displayed + contest entered

set @prev_date_start = unix_timestamp(date_add(curdate(), interval -1 day))*1000;

set @prev_date_end = unix_timestamp(curdate())*1000;

set @prev_cd = date_format(date(from_unixtime(@prev_date_start/1000)), '%Y%m%d');


drop table if exists cdisp;
create temporary table cdisp (key (userID, application)) as
SELECT DISTINCT
    profileID as userID, campGroup, cr.application
FROM
    campaignEvents
        INNER JOIN
    reporting_viz.campRef cr ON campaignEvents.campaignID = cr.campaignID
WHERE
    campaignEvents.application = app
        AND eventType = 'displayed'
        AND cohortDay = @prev_cd
        AND cr.application = app;

IF app in('sainsburys.survey', 'directline')

THEN


drop table if exists cdkeys;
create temporary table cdkeys (key (campGroup, application)) as
SELECT DISTINCT
    foreignKey AS userID, campGroup, cdisp.application
FROM
    foreignKeys
        INNER JOIN
    cdisp ON cdisp.userID = foreignKeys.profileID
        INNER JOIN
    reporting_viz.ids ON ids.userID = foreignKeys.foreignKey;

-- Food
insert ignore into reporting_viz.uxFunnel
SELECT 
    userID, 'Viewed Food Panel', app
FROM
    cdkeys
WHERE
    campGroup = 'Food'
    and application = app;

-- Activities
insert ignore into reporting_viz.uxFunnel
SELECT 
    userID, 'Viewed Activities Panel', app
FROM
    cdkeys
WHERE
    campGroup = 'Activities'
    and application = app;

-- Results
insert ignore into reporting_viz.uxFunnel
SELECT 
    userID, 'Received Result Persona', app
FROM
    cdkeys
WHERE
    campGroup = 'Result Personas'
    and application = app;


-- Get contestants
insert ignore into reporting_viz.uxFunnel
SELECT DISTINCT
    foreignKey, 'Entered Contest', app
FROM
    (SELECT DISTINCT
        profileID
    FROM
        profileEvents
    WHERE
        application = app
            AND eventType = 'contestEntererd'
            AND creation BETWEEN @prev_date_start AND @prev_date_end
            AND eventValue = 'spring2017') AS ce
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = ce.profileID
        INNER JOIN
    reporting_viz.ids ON ids.userID = foreignKeys.foreignKey;

COMMIT;


ELSEIF app = 'regentst'

THEN


-- Food
insert ignore into reporting_viz.uxFunnel
(SELECT 
    userID, 'Viewed Food Panel', app
FROM
    cdisp
WHERE
    campGroup = 'Food'
    and application = app);

-- Activities
insert ignore into reporting_viz.uxFunnel
(SELECT 
    userID, 'Viewed Activities Panel', app
FROM
    cdisp
WHERE
    campGroup = 'Activities'
    and application = app);

-- Results
insert ignore into reporting_viz.uxFunnel
(SELECT 
    userID, 'Received Result Persona', app
FROM
    cdisp
WHERE
    campGroup = 'Result Personas'
    and application = app);


-- Get contestants
insert ignore into reporting_viz.uxFunnel
(SELECT DISTINCT
    profileID, 'Entered Contest', app
FROM
    profileEvents
WHERE
    application = app
        AND eventType = 'contestEntererd'
        AND creation BETWEEN @prev_date_start AND @prev_date_end
        AND eventValue = 'spring2017');


COMMIT;


ELSE

SELECT 'unknown app, revise procedure';

END IF;


END