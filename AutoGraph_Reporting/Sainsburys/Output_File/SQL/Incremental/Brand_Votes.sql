-- Sainsburys incremental brand votes
-- Only change brand votes in the existing spectrum file if the existing spectrum changes. Otherwise, who cares?

-- Get max vote time per brand, per spec profile
drop table if exists sbv;
create table sbv (constraint pk primary key (profileID, brandID, updateID)) as
SELECT 
    foreignKey,
    ifkf.profileID,
    brandID,
    MAX(brandVotes.updateID) AS updateID
FROM
    ifkf
        INNER JOIN
    brandVotes ON brandVotes.profileID = ifkf.profileID
    AND brandVotes.updateID <= ifkf.updateID
GROUP BY foreignKey, ifkf.profileID , brandID;

drop table if exists ifkf;

-- Get most recent votes
drop table if exists sbvotes;
create table sbvotes (key (brandID)) as
SELECT 
    foreignKey, sbv.profileID, sbv.brandID, vote
FROM
    sbv
        INNER JOIN
    brandVotes ON brandVotes.profileID = sbv.profileID
        AND brandVotes.brandID = sbv.brandID
        AND brandVotes.updateID = sbv.updateID;

drop table if exists sbv;
        
-- Get readable brand names
drop table if exists bn;
create table bn (primary key (brandID)) as
SELECT DISTINCT
    brandID, CONCAT('votes:', LOWER(name)) AS Brand
FROM
    brands
WHERE
    application = 'sainsburys.survey';


-- Get brand votes data
SELECT 
    foreignKey, Brand, vote
FROM
    bn
        INNER JOIN
    sbvotes ON sbvotes.brandID = bn.brandID;