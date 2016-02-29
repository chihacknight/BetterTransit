FROM debian:sid

MAINTAINER Tristan Crockett <tristan.h.crockett@gmail.com>

RUN groupadd -r transit && useradd -r -g transit transit

RUN \
  apt-get update && \
  apt-get install -y wget unzip git
RUN mkdir /app
RUN mkdir /app/data && chown transit:transit /app/data
VOLUME /app/data
WORKDIR /app
RUN wget http://gtfs.s3.amazonaws.com/chicago-transit-authority_20121108_0426.zip
RUN unzip chicago-transit-authority_20121108_0426.zip

RUN apt-get install -y postgresql-client
RUN apt-get install -y python2.7
RUN apt-get install -y python-psycopg2
RUN apt-get install -y python-geojson

RUN git clone https://github.com/thcrock/gtfs_SQL_IMPORTER.git

COPY import.sh ./
COPY create_foia_table.sql ./
COPY create_segment_ridership.sql ./
COPY join_riders_using_gtfs.py ./
COPY create_geojson.py ./
COPY run.sh ./

RUN chmod +x import.sh
RUN chmod +x run.sh
RUN wget https://raw.githubusercontent.com/chihacknight/BetterTransit/master/ridership-data/CTA%20original%20bus%20ridership%20data%20for%20October%202012.csv
RUN sed -i -e "1d" 'CTA original bus ridership data for October 2012.csv'
