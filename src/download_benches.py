"""
Quelques liens de ressources:

https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_bbox
https://wiki.openstreetmap.org/wiki/FR:Tag:amenity%3Dbench
"""

import pandas as pd
import osmnx as ox

# France bounding box (too big)
# lat=51.23290 lon=-5.37807
# lat=41.78629 &lon=8.34146
# 9.44661  13.72

def iter_on_bbox(lat_start, lat_end, long_start, long_end, step):
    lat_cur = lat_start
    long_cur = long_start
    while lat_cur <= lat_end:
        while long_cur <= long_end:
            yield(long_cur, lat_cur, long_cur + step, lat_cur + step)
            long_cur += step
        lat_cur += step

def fetch_bench(bbox, tags, default_backrest=None):

    try:
        benches = ox.features.features_from_bbox(bbox, tags)
    except ox._errors.InsufficientResponseError:
        return None

    benches.reset_index(inplace=True)
    try:
        benches["latitude"] = benches["geometry"].y
        benches["longitude"] = benches["geometry"].x
    except:
        # TODO: Il faut gérer les LINESTRING, et peut-être d'autres type d'objets.
        print("FAIL!")
        print(benches["geometry"])
        return None

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


def main():

    #for bbox in iter_on_bbox(41.78629, 51.23290, -5.37807, 8.34146, 0.1):
    #    print(bbox)

    bench_groups = []

    for bbox in iter_on_bbox(41.78629, 42.23290, -5.37807, 8.34146, 0.1):
        benches = fetch_bench(
            bbox,
            # (2.18036, 43.56976, 2.29134, 43.63856),
            {"amenity": "bench"}
            # {"amenity": "lounger"}
        )
        if benches is not None:
            print(int(bbox[0]), int(bbox[1]), len(benches))
            bench_groups.append(benches)

    complete_benches = pd.concat(bench_groups)
    # print(list(complete_benches["id"]))
    complete_benches.drop_duplicates(subset=["id"], inplace=True)
    print(complete_benches)
    # print(list(complete_benches["id"]))
    complete_benches.to_csv("benches.csv", index=False)


if __name__ == "__main__":
    main()
