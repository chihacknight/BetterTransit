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

export.sql takes the table created by snap_gtfs.py and exports it to a CSV file suitable for upload to CartoDB.
