select ctastopid stop_id, street on_street, cross_st cross_street, routea route, direction,
round(on_rte,1) boardings, round(off_rte,1) alightings,
pickname month_beginning, daytype, lat, lon
from rbs_7030_result_day
where pickname='October 2012'
and daytype='Weekday'