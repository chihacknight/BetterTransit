from sqlalchemy import (
    BigInteger,
    Column,
    create_engine,
    MetaData,
    Numeric,
    String,
    Table
)


def ensure_schema(engine):
    meta = MetaData()
    Table(
        'node_pair_ridership',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('route', String),
        Column('direction', String),
        Column('date', String),
        Column('run_id', BigInteger),
        Column('passengers_on', Numeric)
    )

    Table(
        'way_ridership',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('route', String),
        Column('direction', String),
        Column('date', String),
        Column('run_id', BigInteger),
        Column('passengers_on', Numeric),
        Column('osm_way_id', BigInteger),
        Column('tags', String)
    )

    Table(
        'daily_ridership',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('osm_way_id', BigInteger),
        Column('date', String),
        Column('daily_ridership', Numeric),
        Column('routes', String),
        Column('tags', String)
    )

    Table(
        'average_daily_ridership',
        meta,
        Column('begin_node', BigInteger),
        Column('end_node', BigInteger),
        Column('osm_way_id', BigInteger),
        Column('avg_daily_ridership', Numeric),
        Column('routes', String),
        Column('tags', String)
    )

    meta.create_all(engine)


def load_node_pair_ridership(engine, input_filename):
    with open(input_filename) as f:
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.execute('truncate node_pair_ridership')
        cur.copy_from(f, 'node_pair_ridership', sep=',')
        conn.commit()


def compute_way_ridership(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate way_ridership')
    conn.cursor().execute('''
insert into way_ridership
select
    begin_node,
    end_node,
    route,
    direction,
    date,
    run_id,
    max(passengers_on) passengers_on,
    max(planet_osm_ways.id) osm_way_id,
    max(planet_osm_ways.tags) tags
from
    node_pair_ridership
    left join planet_osm_ways
        on (nodes @> ARRAY[begin_node] and nodes @> ARRAY[end_node])
    group by begin_node, end_node, route, direction, date, run_id
''')
    conn.commit()


def compute_daily_ridership(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate daily_ridership')
    conn.cursor().execute('''
insert into daily_ridership
select
    begin_node,
    end_node,
    max(osm_way_id),
    date,
    sum(passengers_on) daily_ridership,
    string_agg(distinct route, ',') routes,
    max(tags) tags
from way_ridership
group by 1, 2, 4 order by 5 desc
''')
    conn.commit()


def compute_avg_daily_ridership(engine):
    conn = engine.raw_connection()
    conn.cursor().execute('truncate average_daily_ridership')
    conn.cursor().execute('''
insert into average_daily_ridership
select
    begin_node,
    end_node,
    max(osm_way_id) osm_way_id,
    avg(daily_ridership) avg_daily_ridership,
    max(routes) routes,
    max(tags) tags
from daily_ridership
group by 1, 2 order by 4 desc
''')
    conn.commit()


def export(engine, output_filename):
    with open(output_filename, 'wb') as f:
        conn = engine.raw_connection()
        cur = conn.cursor()
        cur.copy_to(f, 'average_daily_ridership', sep=',')


def process(input_filename):
    engine = create_engine("postgresql://transit:transit@127.0.0.1/transit")
    ensure_schema(engine)
    load_node_pair_ridership(engine, input_filename)
    compute_way_ridership(engine)
    compute_daily_ridership(engine)
    compute_avg_daily_ridership(engine)
    export(engine, 'average_daily_ridership.csv')
