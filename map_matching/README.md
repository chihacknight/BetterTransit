Requirements:

- Open Source Routing Machine server running at 127.0.0.1:5000
- Postgres database with OpenStreetMap extract loaded in

The process has been rewritten to all be triggered via one entrypoint: run.py
It takes in one argument so far: the input file of some subset of the APC readings.

`python run.py --input-file apc_points.csv`

The script will output a file, `average_daily_ridership.csv`

* Snapping GTFS data *

There is another script in here to snap GTFS data to the street grid. It uses the Tuesday schedule, and counts the number of scheduled trips that day per segment.

`python snap_gtfs.py`

It will result in a gtfs_ways.csv output file. For intermediate processing, it requires:

1. A GTFS extract loaded into Postgres
2. An OSM extract loaded into Postgres, with --slim option in osm2pgsql to create the intermediate tables 'planet_osm_nodes' and 'planet_osm_ways'
