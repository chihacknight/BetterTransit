create table segments_with_ids as (
	with segments as (
		select
			round(start.shape_pt_lat::numeric, 4) as start_lat,
			round(start.shape_pt_lon::numeric, 4) as start_lon,
			round(stop.shape_pt_lat::numeric, 4) as stop_lat,
			round(stop.shape_pt_lon::numeric, 4) as stop_lon
		from
			gtfs_shapes start
			join gtfs_shapes stop on (
				start.shape_id = stop.shape_id and
				start.shape_pt_sequence = stop.shape_pt_sequence - 1
			)
	)
	select
		distinct(start_lat || ',' || start_lon || ' -> ' || stop_lat || ',' || stop_lon) as segment_id,
		segments.*
		from segments
);
