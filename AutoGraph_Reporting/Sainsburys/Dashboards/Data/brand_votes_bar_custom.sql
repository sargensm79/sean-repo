SELECT 
    bv1.brand AS ref_brand,
    bv1.Category AS ref_category,
    bv1.vote AS ref_vote,
    ids.Date,
    ids.userID AS foreignKey,
    bv2.brand,
    bv2.vote
FROM
    bvRef bv1
        INNER JOIN
    bvRef bv2 ON bv1.userID = bv2.userID
        AND bv1.Category = bv2.Category
        INNER JOIN
	ids ON bv1.userID = ids.userID
WHERE application = 'sainsburys.survey'