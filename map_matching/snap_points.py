'''
    snapped_points takes an input file of APC data, and snaps the raw data to
    the street grid. It does this by:

    1. Grouping the points into individual bus runs using the given run ids
    2. Running the initially time-ordered readings through a minimum
        spanning tree
    3. Snap each bus run to the street grid using OSRM, iteratively
        increasing tolerance radius to snap more points
'''
from __future__ import print_function
import csv
import pandas
import requests
from reorder import reorder

BEGINNING_RADIUS = 10


def snap(coord_string, radii):
    options = {
        'radiuses': ';'.join(radii),
        'geometries': 'geojson',
        'annotations': 'true',
        'overview': 'full',
    }
    final_string = 'http://127.0.0.1:5000/match/v1/bus/{}'.format(coord_string)
    r = requests.get(final_string, params=options)
    return r.json()


def iterative_snap(lats, lons, run_id, log_file):
    coord_string = ';'.join(
        "%s,%s" % (lon, lat) for lat, lon in zip(lats, lons)
    )
    radii = [str(BEGINNING_RADIUS)] * len(lats)
    output = None
    for accuracy in range(BEGINNING_RADIUS + 1, BEGINNING_RADIUS + 30):
        output = snap(coord_string, radii)
        if 'tracepoints' not in output:
            raise IOError(output)
        unsnapped_points = []
        for index, tracepoint in enumerate(output['tracepoints']):
            if not tracepoint:
                radii[index] = str(accuracy)
                unsnapped_points.append(index)
        if len(unsnapped_points) == 0:
            print('snapped', run_id, 'at', accuracy, file=log_file)
            return output
    print(
        'gave up', run_id, 'with', len(unsnapped_points),
        'all good besides first and last?',
        all(output['tracepoints'][1:-1]), file=log_file
    )
    return output


def create_dataframe(input_file):
    HEADER = [
        'id',
        'route',
        'dir',
        'busid',
        'date',
        'time',
        'passengers_on',
        'passengers_off',
        'passengers_in',
        'lat',
        'lon'
    ]

    return pandas.read_csv(
        input_file,
        header=None,
        names=HEADER
    )


def sort_readings(readings):
    almost_sorted = readings.sort('time')
    indices = reorder(almost_sorted.as_matrix(), 10, 9)
    return almost_sorted.iloc[indices]


def snapped_points(input_file):
    output_file = open('snapped_output.csv', 'w')
    writer = csv.writer(output_file)

    error_file = open('unsnappable_points.csv', 'w')
    error_writer = csv.writer(error_file)

    log_file = open('snaplog.txt', 'w', 1)

    dataframe = create_dataframe(input_file)

    for run_id, readings in dataframe.groupby('id', sort=False):
        sorted_readings = sort_readings(readings)

        lats = sorted_readings['lat'].tolist()
        lons = sorted_readings['lon'].tolist()
        dates = sorted_readings['date'].tolist()

        output = iterative_snap(lats, lons, run_id, log_file)

        for route, dir, date, lat, lon, passengers_in, tracepoint in zip(
            sorted_readings['route'].tolist(),
            sorted_readings['dir'].tolist(),
            dates,
            lats,
            lons,
            sorted_readings['passengers_in'].tolist(),
            output['tracepoints']
        ):
            if tracepoint:
                match = output['matchings'][tracepoint['matchings_index']]
                legs = match['legs']
                if tracepoint['waypoint_index'] == len(legs):
                    continue
                leg = legs[tracepoint['waypoint_index']]
                nodes = leg['annotation']['nodes']
                args = [
                    ';'.join([str(node) for node in nodes]),
                    route,
                    dir,
                    date,
                    run_id,
                    round(passengers_in, 1),
                    tracepoint['matchings_index'],
                    tracepoint['waypoint_index']
                ]
                writer.writerow(args)
                yield args
            else:
                error_writer.writerow([route, dir, date, run_id, lon, lat])
    output_file.close()
    error_file.close()
    log_file.close()
