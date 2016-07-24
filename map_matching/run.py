import argparse
from snap_points import snapped_points
from reduce_points import reduced_points
from compute_ridership import process

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a bus APC data file')
    parser.add_argument('--input-file', help='input file of bus APC readings')
    args = parser.parse_args()

    file_to_load = reduced_points(snapped_points(args.input_file))
    process(file_to_load)
