#!/bin/sh

./import.sh
cat create_foia_table.sql | psql -h db -U postgres transit
cat CTA\ original\ bus\ ridership\ data\ for\ October\ 2012.csv | psql -h db -U postgres -c 'COPY foia_data from stdin csv' transit
cat create_segment_ridership.sql | psql -h db -U postgres transit
python2.7 join_riders_using_gtfs.py
python2.7 create_geojson.py
