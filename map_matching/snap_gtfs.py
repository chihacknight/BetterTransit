from sqlalchemy import (
    BigInteger,
    Column,
    create_engine,
    Integer,
    MetaData,
    String,
    Table
)
from snap_points import snap


def ensure_schema(engine):
    meta = MetaData()
    Table(
        'gtfs_node_pairs',
        meta,
        Column('shape_id', String),
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('num_trips', Integer),
        Column('routes', String),
    )
    meta.create_all(engine)

if __name__ == '__main__':
    engine = create_engine("postgresql://transit:transit@127.0.0.1/transit")
    ensure_schema(engine)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute("""
    select
        shape_id,
        array_agg(shape_pt_lat order by shape_pt_sequence asc) as lats,
        array_agg(shape_pt_lon order by shape_pt_sequence asc) as lons,
        max(num_trips) as num_trips,
        max(routes) as routes
    from gtfs_shapes
    join (
        select
            distinct(shape_id) as shape_id,
            count(distinct trip_id) as num_trips,
            string_agg(distinct route_id, ',') as routes
        from
            gtfs_trips
            join gtfs_calendar on (gtfs_trips.service_id = gtfs_calendar.service_id and tuesday = 1)
            where route_id not in ('Blue', 'Red', 'Brn', 'P', 'Y', 'Pink', 'Org', 'G')
            group by 1
    ) distinct_shapes using (shape_id)
    group by shape_id
    """)
    result = cursor.fetchall()
    for shape_id, lats, lons, num_trips, routes in result:
        print shape_id
        print len(lats)
        coord_string = ';'.join(
            "%s,%s" % (lon, lat) for lat, lon in zip(lats, lons)
        )
        output = snap(coord_string, ['20' for _ in lats])
        shape_nodes = []
        if 'tracepoints' in output:
            print 'got tracepoints'
            for lat, lon, tracepoint in zip(
                lats,
                lons,
                output['tracepoints']
            ):
                if tracepoint:
                    match = output['matchings'][tracepoint['matchings_index']]
                    legs = match['legs']
                    if tracepoint['waypoint_index'] == len(legs):
                        continue
                    leg = legs[tracepoint['waypoint_index']]
                    nodes = leg['annotation']['nodes']
                    for node in nodes:
                        if node not in shape_nodes:
                            shape_nodes.append(node)
            for i in range(0, len(shape_nodes)-1, 1):
                cursor.execute(
                    'insert into gtfs_node_pairs values (%s, %s, %s, %s, %s)',
                    (shape_id, shape_nodes[i], shape_nodes[i+1], num_trips, routes)
                )
        else:
            print 'did not', output
    connection.commit()
