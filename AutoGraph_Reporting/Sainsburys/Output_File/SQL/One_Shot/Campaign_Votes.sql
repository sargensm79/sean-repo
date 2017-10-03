-- SBS campaign votes for spectrum purposes
-- Classify each profile's most recent vote based on their total number of votes on that campaign

SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

SET @beginning = '20170916'; -- Start date of the project

SET @ending = '20170930';

-- Get count of votes per campaign by profile
-- The number of votes determines where they are in the "vote cycle" forced by the UX
-- E.g. 3 votes on a campaign = a score of 0 (since the cycle goes +1 --> -1 --> 0)
-- See the "vote_recalc" function for the specific classification rules

drop table if exists vote_count;
create temporary table vote_count (key (profileID, campaignID), key(campaignID)) AS
SELECT 
    foreignKey,
    jpref.profileID,
    campaignID,
    COUNT(campaignID) AS vote_count
FROM
    campaignVotes
        INNER JOIN
    jpref ON jpref.profileID = campaignVotes.profileID
        AND campaignVotes.updateID <= jpref.updateID
WHERE
    application = 'sainsburys.survey'
        AND cohortDay BETWEEN @beginning AND @ending
GROUP BY foreignKey , jpref.profileID , campaignID;


-- Convert counts to vote scores
-- Join to FKs/readable titles
SELECT 
    foreignKey,
    CONCAT('campaign_votes:', cr.campaignID) AS Title,
    VOTE_RECALC(vote_count) AS vote
FROM
    vote_count
        INNER JOIN
    reporting_viz.campRef cr ON cr.campaign_id = vote_count.campaignID