from gpx_parser import gpx_to_csv
from analiser import (
    create_track_dataframe,
    add_angles_betwen_segments,
    add_vector_segments,
    add_arc_lengths_betwen_segments,
    add_arc_distances_from_start,
    add_distances_from_start,
    add_oriented_angles_betwen_segments,
    add_velocities,
    make_plot,
    make_pairplt,
)

def main():
    gpx_to_csv("Korotkov_2023", ["Gvandra"])

    df = create_track_dataframe("кольцо12")
    add_arc_distances_from_start(df)
    add_angles_betwen_segments(df)
    add_arc_lengths_betwen_segments(df)
    add_arc_distances_from_start(df)

    print(df.head())
    make_pairplt(df)
    # make_plot(df, 'arc_distances_from_start', 'angles_betwen_segments')


if __name__ == "__main__":
    main()
