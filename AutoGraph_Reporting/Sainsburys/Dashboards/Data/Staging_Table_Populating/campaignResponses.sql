-- Upsert campaign linkfollows + persona displays
-- linkFollowed, displayed

CREATE DEFINER=`root`@`%` PROCEDURE `campaign_responses`(IN app VARCHAR(32))
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 

    ROLLBACK;

    insert into reporting_viz.procedureErrors (
    select now(), 'campaign_response', app
    );

START TRANSACTION;

# Upsert campaign linkfollows + persona displays
# linkFollowed, displayed

set @prev_cd = date_format(date_add(curdate(), interval -1 day), '%Y%m%d');


-- Next, displays/linkfollows (insert/ignore, no upsert round these parts)
-- What happens if a fk follows different links/displays different results personas?
-- Can figure that out later, I guess. Will probably end up being more granular of a process

-- FK apps

IF app in('sainsburys.survey', 'directline')

THEN

insert ignore into reporting_viz.campaignResponse
SELECT DISTINCT
    foreignKey AS userID, Title, eventType AS response
FROM
    campaignEvents
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = campaignEvents.profileID
        INNER JOIN
    reporting_viz.campRef cr ON cr.campaignID = campaignEvents.campaignID
        INNER JOIN
    reporting_viz.ids ON ids.userID = foreignKeys.foreignKey
WHERE
    campaignEvents.application = app
        AND campaignEvents.cohortDay = @prev_cd
        AND eventType IN ('displayed' , 'linkFollowed')
        AND campGroup = 'Result Personas';

COMMIT;

ELSEIF app = 'regentst'

THEN

insert ignore into reporting_viz.campaignResponse
(SELECT DISTINCT
    profileID AS userID, Title, eventType AS response
FROM
    campaignEvents
        INNER JOIN
    reporting_viz.campRef cr ON cr.campaignID = campaignEvents.campaignID
WHERE
    campaignEvents.application = app
        AND campaignEvents.cohortDay = @prev_cd
        AND eventType IN ('displayed' , 'linkFollowed')
        AND campGroup = 'Result Personas');

COMMIT;

ELSE

SELECT 'unknown app, revise procedure';

END IF;

END