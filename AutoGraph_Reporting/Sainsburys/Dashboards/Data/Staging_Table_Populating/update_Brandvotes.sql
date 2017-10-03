-- Upsert most recent brand votes / profile

CREATE DEFINER=`root`@`%` PROCEDURE `update_bvRef`(IN app VARCHAR(32))
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 

    ROLLBACK;

    insert into reporting_viz.procedureErrors (
    SELECT NOW(), 'update_bvRef', app
    );

START TRANSACTION;

#Update bvRef
set @prev_date = date_add(curdate(), interval -1 day);
set @prev_cd = date_format(@prev_date, '%Y%m%d');


IF app IN('sainsburys.survey', 'directline')

THEN

-- Most recent vote (+ vote time) per brand by agID
-- Join to get FKs as well
DROP TABLE IF EXISTS pbv;
CREATE TABLE pbv (key (foreignKey, profileID, updateID)) as
SELECT 
    foreignKey, bv.profileID, bc.brand, Category, bv.updateID, vote
FROM
    (SELECT 
        profileID, brandID, MAX(updateID) AS updateID
    FROM
        brandVotes
    WHERE
        application = app
            AND cohortDay = @prev_cd
    GROUP BY profileID , brandID) AS bv
        INNER JOIN
    brandVotes ON brandVotes.profileID = bv.profileID
        AND brandVotes.brandID = bv.brandID
        AND brandVotes.updateID = bv.updateID
        INNER JOIN
    foreignKeys ON foreignKeys.profileID = bv.profileID
        AND foreignKey != ''
        INNER JOIN
    reporting_viz.brandCategories bc ON bc.brandID = bv.brandID
        AND bc.application = app;
        
        
-- Get most recent votes / profileID / FK
drop table if exists fk_profiles;
create temporary table fk_profiles (key (foreignKey, profileID)) as
SELECT 
    fkp.foreignKey, profileID
FROM
    pbv
        INNER JOIN
    (SELECT 
        foreignKey, MAX(updateID) AS updateID
    FROM
        pbv
    GROUP BY foreignKey) AS fkp ON fkp.foreignKey = pbv.foreignKey
        AND fkp.updateID = pbv.updateID
        INNER JOIN
    reporting_viz.ids ON ids.userID = pbv.foreignKey;


INSERT INTO reporting_viz.bvRef
SELECT 
    fk_profiles.foreignKey, brand, Category, vote
FROM
    fk_profiles
        INNER JOIN
    pbv ON pbv.foreignKey = fk_profiles.foreignKey
        AND pbv.profileID = fk_profiles.profileID
ON DUPLICATE KEY UPDATE bvRef.vote = vote;



DROP TABLE pbv;

COMMIT;


ELSEIF app = 'regentst'

THEN

insert into reporting_viz.bvRef
(SELECT 
    bv.profileID, bv.brand, Category, vote
FROM
    (SELECT 
        profileID, brandID, MAX(updateID) AS updateID
    FROM
        brandVotes
    WHERE
        application = app
            AND cohortDay = @prev_cd
    GROUP BY profileID , brandID) AS bv
        INNER JOIN
    brandVotes ON brandVotes.profileID = bv.profileID
        AND brandVotes.brandID = bv.brandID
        AND brandVotes.updateID = bv.updateID
        INNER JOIN
    reporting_viz.brandCategories bc ON bc.brandID = bv.brandID
        AND bc.application = app)
ON DUPLICATE KEY UPDATE bvRef.vote = vote;

COMMIT;


ELSE

SELECT 'unknown app, revise procedure';

END IF;


END