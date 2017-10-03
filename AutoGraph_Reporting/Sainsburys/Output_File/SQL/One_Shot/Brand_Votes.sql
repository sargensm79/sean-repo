-- Brand votes for Sainsbury's spectrum

SET autocommit = 1;

SET @beginning = '20170916';

SET @ending = '20170930';

-- Get most recent vote time per brand per profile
drop table if exists bt;
create temporary table bt (key (profileID, brandID, updateID)) as
SELECT 
    foreignKey,
    jpref.profileID,
    brandID,
    MAX(brandVotes.updateID) AS updateID
FROM
    brandVotes
        INNER JOIN
    jpref ON jpref.profileID = brandVotes.profileID
        AND brandVotes.updateID <= jpref.updateID
WHERE
    application = 'sainsburys.survey'
        AND cohortDay BETWEEN @beginning AND @ending
GROUP BY foreignKey , jpref.profileID , brandID;

-- Get most recent votes per brandID per profileID
drop table if exists bvotes;
create temporary table bvotes (key (brandID)) as
SELECT
    foreignKey, 
    bt.profileID,
    bt.brandID,
    vote
FROM
    bt
        INNER JOIN
    brandVotes ON brandVotes.profileID = bt.profileID
        AND brandVotes.brandID = bt.brandID
        AND brandVotes.updateID = bt.updateID;

-- Gather/index Sainsbury's brandIDs and their readable names
drop table if exists bn;
create temporary table bn (primary key (brandID)) as
SELECT DISTINCT
    brandID, name AS Brand
FROM
    brands
WHERE
    application = 'sainsburys.survey';

SELECT
    foreignKey,
    CONCAT('votes:', LOWER(Brand)),
    vote
FROM
    bvotes
        INNER JOIN
    bn ON bn.brandID = bvotes.brandID