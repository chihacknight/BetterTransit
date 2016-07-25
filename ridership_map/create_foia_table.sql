create table if not exists foia_data (
	stop_id varchar,
	on_street varchar,
	cross_street varchar,
	route varchar,
	direction varchar,
	boardings float,
	alightings float,
	month_beginning varchar,
	daytype varchar,
	lat varchar,
	lon varchar
);
create index foia_direction on foia_data(direction);
create index foia_route on foia_data(route);
create index foia_stop on foia_data(stop_id);
COPY foia_data from '/app/CTA original bus ridership data for October 2012.csv';
