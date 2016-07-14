'''
    reduced_points exists primarily to convert a nodestring with an arbitrary
    sequential number of nodes into sequential pairs. It does this for each
    input row

    If the input list has two rows, each with a nodestring with seven nodes,
    the output list should have twelve pair rows, as each group of seven
    will produce six distinct pairs.
'''

import csv

FILENAME = 'reduced_output.csv'


def reduced_points(snapped_points):
    output_file = open(FILENAME, 'w')
    writer = csv.writer(output_file)

    prev_node = None
    prev_route = None
    prev_direction = None
    prev_run_id = None
    prev_date = None
    prev_time = None
    nodes_in_run = set()

    for row in snapped_points:
        node_string, route, direction, date, time, run_id, passengers_on, _, _ = row
        if(
            route != prev_route or
            direction != prev_direction or
            run_id != prev_run_id or
            date != prev_date or
            time != prev_time
        ):
            prev_node = None
        if run_id != prev_run_id:
            nodes_in_run = set()
        nodes = node_string.split(';')

        for node in nodes:
            if(
                prev_node is not None and
                node is not None and
                prev_node != node and
                node not in nodes_in_run
            ):
                args = [
                    prev_node,
                    node,
                    route,
                    direction,
                    date,
                    time,
                    run_id,
                    passengers_on
                ]
                writer.writerow(args)
            prev_node = node
            nodes_in_run.add(node)

        prev_route = route
        prev_direction = direction
        prev_run_id = run_id
        prev_date = date
        prev_time = time
    return FILENAME
