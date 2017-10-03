-- Incremental campaign votes

-- Get count of votes per campaign by spectrum-updated profile/FK
-- The number of votes determines where they are in the "vote cycle" forced by the UX
-- E.g. 3 votes on a campaign = a score of 0 (since the cycle goes +1 --> -1 --> 0)
-- See the "mod_test" function for the specific classification rules
drop table if exists vote_counts;
create temporary table vote_counts (constraint pk primary key (profileID, campaignID), key(campaignID)) as
SELECT 
    foreignKey,
    ifkf.profileID,
    campaignID,
    COUNT(campaignID) AS vote_count
FROM
    ifkf
        INNER JOIN
    campaignVotes cv ON cv.profileID = ifkf.profileID
    AND campaignVotes.updateID <= ifkf.updateID
GROUP BY foreignKey , ifkf.profileID , campaignID;

-- Convert counts to vote scores
-- Join to readable titles
SELECT 
    foreignKey, Title, MOD_TEST(vote_count) AS vote
FROM
    vote_counts
        INNER JOIN
    reporting_viz.campRef cr ON cr.campaignID = vote_counts.campaignID;