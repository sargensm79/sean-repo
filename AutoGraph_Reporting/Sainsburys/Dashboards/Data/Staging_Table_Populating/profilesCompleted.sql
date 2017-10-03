-- Insert profiles that were completed into uxFunnel table
CREATE DEFINER=`root`@`%` PROCEDURE `profiles_completed`(IN app VARCHAR(32))
BEGIN


    DECLARE EXIT HANDLER FOR SQLEXCEPTION 

    ROLLBACK;

    insert into reporting_viz.procedureErrors (
    select now(), 'profiles_completed', app
    );

START TRANSACTION;

# Completed fks

set @prev_cd = date_format(date_add(curdate(), interval -1 day), '%Y%m%d');


drop table if exists pc;
create temporary table pc (primary key (profileID)) as
SELECT DISTINCT
    profileID
FROM
    profileSpectrums
WHERE
    cohort = @prev_cd;


IF app in('sainsburys.survey', 'directline')

THEN

insert ignore into reporting_viz.uxFunnel
SELECT DISTINCT
    foreignKey, 'Completed Profile', app
FROM
    pc
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = pc.profileID
        INNER JOIN
    reporting_viz.ids ON ids.userID = foreignKeys.foreignKey
WHERE
    application = app AND foreignKey != '';

COMMIT;

ELSEIF app = 'regentst'

THEN

insert ignore into reporting_viz.uxFunnel
(SELECT DISTINCT
    profileID, 'Completed Profile', app
FROM
    pc
        INNER JOIN
    profiles ON profiles.profileID = pc.profileID
WHERE
    application = app);

COMMIT;

ELSE

SELECT 'unknown app, revise procedure';

END IF;

END