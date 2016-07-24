from sqlalchemy import (
    BigInteger,
    Column,
    create_engine,
    MetaData,
    Numeric,
    String,
    Table,
    Text
)


def ensure_schema(engine):
    meta = MetaData()
    Table(
        'node_pair_events',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('route', String),
        Column('direction', String),
        Column('date', String),
        Column('time', String),
        Column('run_id', BigInteger),
        Column('passengers_on', Numeric)
    )

    Table(
        'way_events',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('route', String),
        Column('direction', String),
        Column('date', String),
        Column('time', String),
        Column('run_id', BigInteger),
        Column('passengers_on', Numeric),
        Column('osm_way_id', BigInteger),
        Column('tags', String),
        Column('geometry_geojson', Text)
    )

    Table(
        'way_hourly',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('osm_way_id', BigInteger),
        Column('date', String),
        Column('hour', String),
        Column('ridership', Numeric),
        Column('routes', String),
        Column('tags', String),
        Column('geometry_geojson', Text)
    )

    Table(
        'way_avg_hourly',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('osm_way_id', BigInteger),
        Column('hour', String),
        Column('avg_hourly_ridership', Numeric),
        Column('routes', String),
        Column('tags', String),
        Column('geometry_geojson', Text)
    )

    Table(
        'way_daily',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('osm_way_id', BigInteger),
        Column('date', String),
        Column('daily_ridership', Numeric),
        Column('routes', String),
        Column('tags', String),
        Column('geometry_geojson', Text)
    )

    Table(
        'way_avg_daily',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('osm_way_id', BigInteger),
        Column('avg_daily_ridership', Numeric),
        Column('routes', String),
        Column('tags', String),
        Column('geometry_geojson', Text)
    )

    meta.create_all(engine)


def load_node_pair_events(engine, input_filename):
    with open(input_filename) as f:
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.execute('truncate node_pair_events')
        cur.copy_from(f, 'node_pair_events', sep=',')
        conn.commit()


def compute_way_events(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate way_events')
    conn.cursor().execute('''
insert into way_events
select
    begin_node,
    end_node,
    route,
    direction,
    date,
    time,
    run_id,
    max(passengers_on) passengers_on,
    max(planet_osm_ways.id) osm_way_id,
    max(planet_osm_ways.tags) tags,
    max(st_asgeojson(st_makeline(
        st_transform(
            st_geomfromtext('point('||bnode.lon/100||' '||bnode.lat/100||')', 3785),
            4326
        ),
        st_transform(
            st_geomfromtext('point('||enode.lon/100||' '||enode.lat/100||')', 3785),
            4326
        )
    ))) as geometry_geojson
from
    node_pair_events
    left join planet_osm_ways
        on (nodes @> ARRAY[begin_node] and nodes @> ARRAY[end_node])
    left join planet_osm_nodes bnode on (begin_node = bnode.id)
    left join planet_osm_nodes enode on (end_node = enode.id)
    group by begin_node, end_node, route, direction, date, time, run_id
''')
    conn.commit()


def compute_way_hourly(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate way_hourly')
    conn.cursor().execute('''
insert into way_hourly
select
    begin_node,
    end_node,
    osm_way_id,
    date,
    substring(time from 0 for 3) as hour,
    sum(passengers_on) ridership,
    string_agg(distinct route, ',') routes,
    max(tags),
    max(geometry_geojson)
from
    way_events
    group by begin_node, end_node, osm_way_id, date, hour
''')
    conn.commit()


def compute_way_avg_hourly(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate way_avg_hourly')
    conn.cursor().execute('''
insert into way_avg_hourly
select
    begin_node,
    end_node,
    osm_way_id,
    hour,
    avg(ridership) avg_hourly_ridership,
    max(routes) routes,
    max(tags) tags,
    max(geometry_geojson) geometry_geojson
from way_hourly
group by 1, 2, 3, 4 order by 5 desc
''')
    conn.commit()


def compute_way_daily(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate way_daily')
    conn.cursor().execute('''
insert into way_daily
select
    begin_node,
    end_node,
    max(osm_way_id),
    date,
    sum(ridership) daily_ridership,
    max(routes) routes,
    max(tags) tags,
    max(geometry_geojson) geometry_geojson

from way_hourly
group by 1, 2, 4 order by 5 desc
''')
    conn.commit()


def compute_way_avg_daily(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate way_avg_daily')
    conn.cursor().execute('''
insert into way_avg_daily
select
    begin_node,
    end_node,
    max(osm_way_id) osm_way_id,
    avg(daily_ridership) avg_daily_ridership,
    max(routes) routes,
    max(tags) tags,
    max(geometry_geojson) geometry_geojson
from way_daily
group by 1, 2 order by 4 desc
''')
    conn.commit()


def export(engine, table):
    output_filename = "{}.csv".format(table)
    with open(output_filename, 'wb') as f:
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.copy_to(f, table, sep=',')


def process(input_filename):
    engine = create_engine("postgresql://transit:transit@127.0.0.1/transit")
    ensure_schema(engine)
    load_node_pair_events(engine, input_filename)
    compute_way_events(engine)
    compute_way_hourly(engine)
    compute_way_avg_hourly(engine)
    compute_way_daily(engine)
    compute_way_avg_daily(engine)
    export(engine, 'way_avg_daily')
    export(engine, 'way_avg_hourly')
