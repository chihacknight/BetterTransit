import psycopg2
import csv
import geojson
import argparse
import json

def get_data(cursor):
	sql = '''
select
	begin_lon,
	begin_lat,
	end_lon,
	end_lat,
	(select array_to_json(array_agg(row_to_json(d))) from (
		select route, direction, riders
		from segment_ridership s2
		where s2.begin_lat = s.begin_lat
		and s2.end_lat = s.end_lat
		and s2.begin_lon = s.begin_lon
		and s2.end_lon = s.end_lon
	) d ) as groups,
	sum(riders)
	from segment_ridership s
	group by 1,2,3,4 order by 6 desc
	limit 5000'''
	cursor.execute(sql)
	return list(reversed(cursor.fetchall()))

if __name__ == '__main__':
	conn = psycopg2.connect(database='transit', user='postgres', host='db')
	cursor = conn.cursor()
	results = get_data(cursor)
	features = []
	segment_lookup = {}
	for row in results:
		begin_lon, begin_lat, end_lon, end_lat, ridership_data, total_riders = row
		# GeoJSON for line
		feature = geojson.Feature(
			geometry=geojson.LineString([
				(float(begin_lon), float(begin_lat)),
				(float(end_lon), float(end_lat))
			]),
			properties={'num_passengers': total_riders}
		)
		features.append(feature)

		# Full ridership json for hover
		segment_key = '{},{}->{},{}'.format(begin_lon, begin_lat, end_lon, end_lat)
		segment_lookup[segment_key] = ridership_data
	coll = geojson.FeatureCollection(features)
	with open('data/citywide.geojson', 'wb') as jsonfile:
		jsonfile.write(geojson.dumps(coll))
	with open('data/citywide.json', 'wb') as jsonfile:
		jsonfile.write(json.dumps(segment_lookup))
