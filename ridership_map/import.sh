#!/bin/bash
cd gtfs_SQL_IMPORTER/src
echo 'CREATE DATABASE transit' | psql -h db -U postgres 
cat gtfs_tables.sql \
  <(python2.7 import_gtfs_to_sql.py /app) \
  gtfs_tables_makeindexes.sql \
  vacuumer.sql \
| psql -h db -U postgres transit
