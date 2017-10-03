SELECT 
    cv1.Title AS ref_title,
    cv1.campGroup AS ref_group,
    cv1.vote AS ref_vote,
    ids.Date,
    ids.userID AS foreignKey,
    cv2.Title,
    cv2.vote AS vote
FROM
    cvRef cv1
        INNER JOIN
    cvRef cv2 ON cv1.userID = cv2.userID
        AND cv1.campGroup = cv2.campGroup
        INNER JOIN
	ids ON cv1.userID = ids.userID
WHERE application = 'sainsburys.survey'