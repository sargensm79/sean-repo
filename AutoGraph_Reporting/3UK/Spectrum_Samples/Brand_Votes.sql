# Brand votes

# Most recent votes per brand per FK
drop table if exists bvotes;
create temporary table bvotes (key (brandID)) as
SELECT 
    fkbv.foreignKey, fkbv.profileID, fkbv.brandID, vote
FROM
    (SELECT 
        foreignKey, fu.profileID, brandID, MAX(updateID) AS updateID
    FROM
        fk_updates fu
    INNER JOIN brandVotes bv ON bv.profileID = fu.profileID
    GROUP BY foreignKey , fu.profileID , brandID) AS fkbv
        INNER JOIN
    brandVotes bvo ON bvo.profileID = fkbv.profileID
        AND bvo.brandID = fkbv.brandID
        AND bvo.updateID = fkbv.updateID;
        

drop table if exists bn;
create temporary table bn (primary key (brandID)) as
SELECT DISTINCT
    brandID, name
FROM
    brands
WHERE
    application = 'threeuk';

DROP TABLE fk_updates;

# Join to get brand names rather than ID
SELECT 
    foreignKey AS AG_ID, name AS BRAND_ID, vote
FROM
    bvotes
        INNER JOIN
    bn ON bn.brandID = bvotes.brandID;