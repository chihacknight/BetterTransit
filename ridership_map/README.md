The ridership map's input data computation process is now automated using Docker. The steps to run are:

- Install Docker ( https://docs.docker.com/engine/installation/ )
- Install Docker-Compose ( https://docs.docker.com/compose/install/ )
- `cd ridership_map`
- `mkdir data`
- `chmod 777 data`
- `docker-compose build` (the path to the docker-compose binary may be different than this, depending on how you installed)
- `docker-compose up`

Both of the last two steps will take a while, as many dependencies will be downloaded and installed during the 'build' command, and a lot of computation will happen during the 'up' command. You should see progress scroll by in your terminal window. Eventually, it should finish and you will have a new .geojson file in your data directory that the map will use.
