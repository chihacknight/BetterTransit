copy (
	select
		begin_node,
		end_node,
		max(planet_osm_ways.id) as way_id,
		sum(num_trips) as num_trips,
		string_agg(distinct routes, ',') as routes,
		string_agg(distinct shape_id, ',') as shapes,
           st_asgeojson(st_makeline(
                   st_transform(
                           st_geomfromtext('point('||bnode.lon/100||' '||bnode.lat/100||')', 3785),
                           4326
                   ),
                   st_transform(
                           st_geomfromtext('point('||enode.lon/100||' '||enode.lat/100||')', 3785),
                           4326
                   )
           )) as geometry_geojson
	from
		gtfs_node_pairs
		join planet_osm_ways on (nodes @> ARRAY[begin_node] and nodes @> ARRAY[end_node])
		left join planet_osm_nodes bnode on (begin_node = bnode.id)
		left join planet_osm_nodes enode on (end_node = enode.id)
	group by 1, 2, 7
	order by 4 desc
) to '/tmp/gtfs_ways.csv' with csv header
