import psycopg2
import csv
import geojson
import argparse

conn = psycopg2.connect(database='transit', user='transit')
cursor = conn.cursor()


def generate_route_dir_combos(cursor):
	cursor.execute('select route_id, direction, route_long_name from gtfs_trips join gtfs_routes using (route_id) group by 1,2,3 order by 1,2')
	return cursor.fetchall()

def most_frequent_shape_and_trip(route, direction, cursor):
	cursor.execute("""
select t.shape_id, count(*), min(t.trip_id) from gtfs_trips t join gtfs_calendar c using (service_id)
where monday = '1' and
route_id = %s and
direction = %s
group by 1
order by 2 desc limit 1
""", (route, direction))
	
	results = cursor.fetchone()
	if results is None:
		return (None, None)
	shape_id = results[0]
	trip_id = results[2]
	#print shape_id, trip_id
	return shape_id, trip_id

def stop_data(trip_id, route, direction, cursor):
	cursor.execute("""
select
	g.stop_id,
	g.stop_sequence,
	f.boardings,
	f.alightings,
	round(s.stop_lat::numeric, 2),
	round(s.stop_lon::numeric, 2),
	s.stop_name
from
	gtfs_stop_times g
	join foia_data f using (stop_id)
	join gtfs_stops s using (stop_id)
where trip_id = %s
and route = %s
and f.direction = %s
order by g.stop_sequence
""", (trip_id, route, direction))

	return cursor.fetchall()

def shape_data(shape_id, cursor):
	cursor.execute("""
select
	shape_id,
	round(shape_pt_lat::numeric, 2),
	round(shape_pt_lon::numeric, 2),
	round(shape_pt_lat::numeric, 5),
	round(shape_pt_lon::numeric, 5),
	shape_pt_sequence
from gtfs_shapes
where shape_id = %s
order by shape_pt_sequence
""", (shape_id,))
	return cursor.fetchall()

def assign_ridership_to_segments(segments, stops, route, direction, cursor):
	stop_index = 0
	running_total = 0
	old_fine_lat = None
	old_fine_lon = None
	raw_features = []
	#print stops[0]
	for segment in segments:
		#print segment
		shape_id, coarse_lat, coarse_lon, fine_lat, fine_lon, segment_sequence = segment
		if stop_index > len(stops)-1:
			continue
		if str(coarse_lat) == str(stops[stop_index][4]) and str(coarse_lon) == str(stops[stop_index][5]):
			stop = stops[stop_index]
			#print stop
			running_total += stops[stop_index][2]
			running_total -= stops[stop_index][3]
			#print running_total, "on the bus at", stops[stop_index][6], fine_lat, fine_lon
			stop_index += 1
		if old_fine_lat is not None:
			#print running_total, "on between", old_fine_lat, old_fine_lon, "and", fine_lat, fine_lon
			pkey_args = (str(old_fine_lon), str(old_fine_lat), str(fine_lon), str(fine_lat), str(route), str(direction))
			#print pkey_args
			cursor.execute('''
delete from segment_ridership
where 
	begin_lon = %s and
	begin_lat = %s and
	end_lon = %s and
	end_lat = %s and
	route = %s and
	direction = %s
''', pkey_args)
			cursor.execute('''
insert into segment_ridership
values (%s, %s, %s, %s, %s, %s, %s)
''', pkey_args + (round(running_total, 1),))
		old_fine_lat = fine_lat
		old_fine_lon = fine_lon
	cursor.execute('commit')

if __name__ == '__main__':
	for route, direction, name in generate_route_dir_combos(cursor):
	#for route, direction in [('30', 'South')]:
		print "analyzing", route, direction, name
		shape_id, trip_id = most_frequent_shape_and_trip(route, direction, cursor)
		if shape_id is None:
			continue
		stops = stop_data(trip_id, route, direction, cursor)
		segments = shape_data(shape_id, cursor)
		assign_ridership_to_segments(segments, stops, route, direction, cursor)
