"""
Quelques liens de ressources:

https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_bbox
https://wiki.openstreetmap.org/wiki/FR:Tag:amenity%3Dbench
"""

import pandas as pd
import osmnx as ox
import shapely

# Rectangle englobant la France (trop gros)
# lat=51.23290 lon=-5.37807
# lat=41.78629 &lon=8.34146

# Rectangle englobant l'Occitanie (trop gros aussi)
# lat=45.017509 &lon=-0.384436
# lat=42.26926  &lon=4.86012

# Rectangle englobant Toulouse, Castres et Albi
# lat=43.96508 &lon=1.17073
# lat=43.47379 &lon=2.39923


def iter_on_bbox(lat_start, lat_end, long_start, long_end, step):
    lat_cur = lat_start
    long_cur = long_start
    while lat_cur <= lat_end:
        while long_cur <= long_end:
            yield(long_cur, lat_cur, long_cur + step, lat_cur + step)
            long_cur += step
        long_cur = long_start
        lat_cur += step


def fetch_bench(bbox, tags, default_backrest=None):

    try:
        benches = ox.features.features_from_bbox(bbox, tags)
    except ox._errors.InsufficientResponseError:
        return None

    benches.reset_index(inplace=True)
    if not set(benches["geometry"].geom_type).issubset({"Point", "LineString", "Polygon"}):
        print(set(benches["geometry"].geom_type))
        print(benches)
        print(benches["geometry"])
        raise Exception("Unexpected geometry type")

    filter_point = benches["geometry"].geom_type == "Point"
    benches.loc[filter_point, "latitude"] = benches[filter_point]["geometry"].y
    benches.loc[filter_point, "longitude"] = benches[filter_point]["geometry"].x

    filter_poly = benches["geometry"].geom_type != "Point"
    benches.loc[filter_poly, "latitude"] = shapely.get_point(benches[filter_poly]["geometry"], 0).y
    benches.loc[filter_poly, "longitude"] = shapely.get_point(benches[filter_poly]["geometry"], 0).x

    if default_backrest is None:
        if "backrest" in benches.columns:
            benches["int_backrest"] = (benches["backrest"] == "yes").astype(int)
        else:
            benches["int_backrest"] = 0
    else:
        benches["int_backrest"] = default_backrest

    benches.drop(
        benches.columns.difference(["id", "latitude", "longitude", "int_backrest"]),
        axis=1,
        inplace=True
    )
    return benches


def fetch_and_save_benches_bbox(main_bbox, tags, csv_file, default_backrest=None):

    bench_groups = []

    iter_params = list(main_bbox) + [0.1]
    for bbox in iter_on_bbox(*iter_params):
        benches = fetch_bench(bbox, tags, default_backrest)
        if benches is not None:
            print(round(bbox[0], 1), round(bbox[1], 1), len(benches))
            bench_groups.append(benches)

    complete_benches = pd.concat(bench_groups)
    complete_benches.drop_duplicates(subset=["id"], inplace=True)
    print(complete_benches)
    complete_benches.to_csv(csv_file, index=False)


def main():
    main_bbox = (43.4, 43.99, 1.1, 2.39)
    fetch_and_save_benches_bbox(main_bbox, {"amenity": "bench"}, "benches.csv")
    fetch_and_save_benches_bbox(main_bbox, {"amenity": "lounger"}, "benches_lounger.csv", 1)
    # On ne mettra pas ces objets dans la carte. Certains n'ont pas de géométrie, et les id ne correspondent pas.
    # Ça mériterait d'être étudié plus attentivement, mais pour une première version, on laisse ça là.
    fetch_and_save_benches_bbox(main_bbox, {"bench": "yes"}, "benches_whatever.csv", 0)


if __name__ == "__main__":
    main()
