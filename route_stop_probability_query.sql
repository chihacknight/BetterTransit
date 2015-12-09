	select
		route_id,
		begin_stop_id,
		end_stop_id,
		round(numerator::numeric / denominator::numeric, 2) as probability
	from (
		select
			stop_trips.route_id,
			gtfs_stop_times.stop_id begin_stop_id,
			stop_trips.stop_id end_stop_id,
			count(distinct gtfs_stop_times.trip_id) numerator,
			max(total_trips) as denominator
		from
			(
				select
					gtfs_trips.route_id,
					gtfs_stop_times.trip_id,
					gtfs_stop_times.stop_id,
					gtfs_stop_times.stop_sequence
				from gtfs_stop_times
				join gtfs_trips using (trip_id)
			) stop_trips 
		join gtfs_stop_times on (
			stop_trips.trip_id = gtfs_stop_times.trip_id and 
			stop_trips.stop_sequence = gtfs_stop_times.stop_sequence - 1)
		join ( select
			route_id,
			stop_id,
			count(distinct gtfs_stop_times.trip_id) as total_trips
				from gtfs_stop_times
				join gtfs_trips using (trip_id)
				group by 1, 2
			) stop_trip_totals on (
				stop_trips.stop_id = stop_trip_totals.stop_id and
				stop_trips.route_id = stop_trip_totals.route_id
			)
		group by 1, 2, 3
		order by 1
	) trip_counts
	limit 5;
