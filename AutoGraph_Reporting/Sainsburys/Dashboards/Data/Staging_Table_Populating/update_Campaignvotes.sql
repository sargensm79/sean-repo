-- Upsert most recent campaign votes / profile

CREATE DEFINER=`root`@`%` PROCEDURE `update_cvRef`(IN app VARCHAR(32))
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 

    ROLLBACK;

    insert into reporting_viz.procedureErrors (
    select now(), 'update_cvRef', app
    );

set @prev_date = date_add(curdate(), interval -1 day);
set @prev_cd = date_format(@prev_date, '%Y%m%d');

START TRANSACTION;

-- Get all profiles and campaign votes from past day (and max vote time/profile/campaign)
drop table if exists prev_day_votes;
create temporary table prev_day_votes (constraint pk primary key (profileID, campaignID)) as
SELECT 
    profileID, campaignID, MAX(updateID) AS updateID
FROM
    campaignVotes
WHERE
    application = app
        AND cohortDay = @prev_cd
GROUP BY profileID , campaignID;


IF app in('sainsburys.survey', 'directline')

THEN


-- Get total count of votes on that campaign per profile
drop table if exists prev_day_counts;
create temporary table prev_day_counts (key (profileID, campaignID, updateID)) as
SELECT 
    pdv.profileID,
    pdv.campaignID,
    pdv.updateID,
    COUNT(pdv.campaignID) AS vote_count
FROM
    prev_day_votes pdv
        INNER JOIN
    campaignVotes cv ON pdv.profileID = cv.profileID
        AND pdv.campaignID = cv.campaignID
WHERE
    application = app
        AND cohortDay BETWEEN '20170915' AND @prev_cd	-- Project start date
GROUP BY pdv.profileID , pdv.campaignID , pdv.updateID;


-- Convert votecounts to vote scores
-- Join to FKs
drop table if exists pcv;
create table pcv (key (foreignKey, profileID, updateID), key(campaignID)) as
SELECT 
    foreignKey,
    pdc.profileID,
    pdc.campaignID,
    vote_recalc(vote_count) AS vote,
    updateID
FROM
    prev_day_counts pdc
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = pdc.profileID
        AND foreignKey != '';


-- Get most recent campaign voting profile per FK
drop table if exists fk_profiles;
create temporary table fk_profiles (key (foreignKey, profileID)) as
SELECT 
    fk_profiles.foreignKey, profileID
FROM
    pcv
        INNER JOIN
    (SELECT 
        foreignKey, MAX(updateID) AS updateID
    FROM
        pcv
    GROUP BY foreignKey) AS fk_profiles ON fk_profiles.foreignKey = pcv.foreignKey
        AND fk_profiles.updateID = pcv.updateID
        INNER JOIN
    reporting_viz.ids ON ids.userID = pcv.foreignKey;


-- select the votes for that profile
-- Join to get readable titles
-- Filter our result persona votes that might sneak in
insert into reporting_viz.cvRef
SELECT 
    fk_profiles.foreignKey, Title, campGroup, vote
FROM
    fk_profiles
        INNER JOIN
    pcv ON pcv.foreignKey = fk_profiles.foreignKey
        AND pcv.profileID = fk_profiles.profileID
        INNER JOIN
    reporting_viz.campRef cr ON cr.campaignID = pcv.campaignID
WHERE
    campGroup != 'Result Personas'
on duplicate key update cvRef.vote = vote;


drop table pcv;

COMMIT;


ELSEIF app = 'regentst'

THEN

insert into reporting_viz.cvRef
(SELECT 
    pdv.profileID, Title, campGroup, vote
FROM
    prev_day_votes pdv
        INNER JOIN
    campaignVotes cv ON cv.profileID = pdv.profileID
        AND cv.campaignID = pdv.campaignID
        AND cv.updateID = pdv.updateID
        INNER JOIN
    reporting_viz.campRef cr ON cr.campaignID = fcm.campaignID
WHERE
    campGroup != 'Result Personas')
on duplicate key update cvRef.vote = vote;

COMMIT;

ELSE

SELECT 'unknown app, revise procedure';

END IF;


END