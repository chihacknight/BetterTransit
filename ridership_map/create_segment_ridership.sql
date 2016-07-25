create table if not exists segment_ridership(
	begin_lon varchar,
	begin_lat varchar,
	end_lon varchar,
	end_lat varchar,
	route varchar,
	direction varchar,
	riders integer,
	primary key (begin_lon, begin_lat, end_lon, end_lat, route, direction)
);
