"""
Quelques liens de ressources:

https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_bbox
https://wiki.openstreetmap.org/wiki/FR:Tag:amenity%3Dbench
"""

import osmnx as ox


def main():

    benches = ox.features.features_from_point((43.61862, 2.25943), {"amenity": "bench"}, 1000 )

    benches.reset_index(inplace=True)
    benches["latitude"] = benches["geometry"].y
    benches["longitude"] = benches["geometry"].x
    benches["int_backrest"] = (benches["backrest"] == "yes").astype(int)
    benches.drop(columns=["element", "amenity", "geometry", "backrest"], inplace=True)

    print(benches.columns)
    print(benches.head())


if __name__ == "__main__":
    main()
