# 3UK incremental brand votes crap

# Get the most recent brand votes per FK
create temporary table bvotes (key (profileID), key(brandID)) as
SELECT 
    bv.profileID, bv.brandID, vote
FROM
    (SELECT 
        kc.profileID, brandID, MAX(brandVotes.updateID) AS updateID
    FROM
        key_creation kc
    INNER JOIN brandVotes ON brandVotes.profileID = kc.profileID
        AND brandVotes.updateID <= kc.updateID
    GROUP BY kc.profileID , brandID) AS bv
        INNER JOIN
    brandVotes ON brandVotes.profileID = bv.profileID
        AND brandVotes.brandID = bv.brandID
        AND brandVotes.updateID = bv.updateID;

# Select key_creation data into temporary table so you don't need another Python cursor
create temporary table key_creation_temp (key (profileID)) as
SELECT 
    *
FROM
    key_creation;

DROP TABLE key_creation;

# Get Irene-readable names
create temporary table bn (primary key (brandID)) as
SELECT DISTINCT
    brandID, name
FROM
    brands
WHERE
    application = 'threeuk';


# Join back to FKs (include spectrum time for correct dataframe join in pandas)
# Join to Irene readable names (join to brand DB for human readable names)
SELECT 
    foreignKey AS 'Foreign Key',
    CONCAT('votes:', LOWER(name)) AS name,
    vote
FROM
    bvotes
        INNER JOIN
    key_creation_temp kc ON kc.profileID = bvotes.profileID
        INNER JOIN
    bn ON bn.brandID = bvotes.brandID
