-- upon move to production - truncate tables and start this procedure

DELIMITER $$

create event sainsburys_refresh
	on schedule
		EVERY 1 Day STARTS '2017-06-15 05:00:00'
	DO BEGIN
		call profiles_created('sainsburys.survey');
        call profiles_completed('sainsburys.survey');
        call funnel_completion('sainsburys.survey');
        call campaign_responses('sainsburys.survey');
        call update_cvRef('sainsburys.survey');
        call update_bvRef('sainsburys.survey');

END $$

DELIMITER ;