"""Check a generated frequency GTFS against params.json.

Fails if route ids do not join, or if configured speeds and headways were
replaced by the defaults.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def gtfs_time_to_sec(value: str) -> int:
    hours, minutes, seconds = (int(part) for part in str(value).split(":"))
    return hours * 3600 + minutes * 60 + seconds


def main() -> int:
    params = json.loads((ROOT / "params.json").read_text(encoding="utf-8"))
    city = params["city"]
    gtfs_dir = ROOT / "data" / city / "gtfs-frequencies"
    processed = ROOT / "data" / city / "processed"

    routes = pd.read_csv(gtfs_dir / "routes.txt")
    trips = pd.read_csv(gtfs_dir / "trips.txt")
    shapes = pd.read_csv(gtfs_dir / "shapes.txt")
    stops = pd.read_csv(gtfs_dir / "stops.txt")
    stop_times = pd.read_csv(gtfs_dir / "stop_times.txt")
    frequencies = pd.read_csv(gtfs_dir / "frequencies.txt")
    import geopandas as gpd

    segments = gpd.read_file(processed / "segments.geojson")

    errors = []

    for column in ("route_id", "route_short_name", "route_long_name", "route_type"):
        if column not in routes.columns:
            errors.append(f"routes.txt missing {column}")
    if "route_name" in routes.columns or "route_name_short" in routes.columns:
        errors.append("routes.txt still uses non-GTFS route_name columns")
    if "route_id" not in trips.columns:
        errors.append("trips.txt missing route_id")
    elif "route_name" in trips.columns:
        errors.append("trips.txt still uses route_name instead of route_id")

    if "route_id" in trips.columns and "route_id" in routes.columns:
        missing_routes = set(trips["route_id"]) - set(routes["route_id"])
        if missing_routes:
            errors.append(f"trips.route_id not in routes.txt: {sorted(missing_routes)[:5]}")
    if "shape_id" in trips.columns:
        missing_shapes = set(trips["shape_id"]) - set(shapes["shape_id"])
        if missing_shapes:
            errors.append(f"trips.shape_id not in shapes.txt: {sorted(missing_shapes)[:5]}")
    missing_stops = set(stop_times["stop_id"]) - set(stops["stop_id"])
    if missing_stops:
        errors.append(f"stop_times.stop_id not in stops.txt: {len(missing_stops)} ids")

    spacing_m = float(params["stops"]["distance_between_stops"])
    speed_table = params["stop_times"]["speed_by_route"]
    speed_default = float(speed_table["default"])
    headway_table = params["frequencies"]["headway_by_route"]
    headway_default = float(headway_table["default"])
    default_headway_secs = int(round(headway_default * 60))

    short_to_id = dict(zip(routes["route_short_name"], routes["route_id"]))
    id_set = set(routes["route_id"])

    def resolve(key: str) -> str | None:
        if key in id_set:
            return key
        if key in short_to_id:
            return short_to_id[key]
        return None

    stop_times = stop_times.copy()
    stop_times["arrival_sec"] = stop_times["arrival_time"].map(gtfs_time_to_sec)
    stop_times["departure_sec"] = stop_times["departure_time"].map(gtfs_time_to_sec)
    by_stop = stop_times.set_index("stop_id")

    for key, minutes in headway_table.items():
        if key == "default":
            continue
        route_id = resolve(key)
        if route_id is None:
            errors.append(f"headway key {key!r} did not match a route")
            continue
        trip_id = f"{route_id}_trip_00"
        rows = frequencies.loc[frequencies["trip_id"] == trip_id, "headway_secs"]
        if rows.empty:
            errors.append(f"no frequency row for {trip_id}")
            continue
        actual = int(rows.iloc[0])
        expected = int(round(float(minutes) * 60))
        if actual != expected:
            errors.append(f"{route_id} headway_secs={actual}, expected {expected}")
        if actual == default_headway_secs and expected != default_headway_secs:
            errors.append(f"{route_id} headway fell back to default {default_headway_secs}")

    full_segments = segments[segments["length_m"].sub(spacing_m).abs() < 1].copy()
    for key, speed in speed_table.items():
        if key == "default":
            continue
        route_id = resolve(key)
        if route_id is None:
            errors.append(f"speed key {key!r} did not match a route")
            continue
        route_segments = full_segments[full_segments["route_name"] == route_id]
        if route_segments.empty:
            errors.append(f"no {spacing_m:.0f} m segment for {route_id}")
            continue
        deltas = []
        for seg in route_segments.itertuples(index=False):
            depart = int(by_stop.loc[seg.from_stop_id, "departure_sec"])
            arrive = int(by_stop.loc[seg.to_stop_id, "arrival_sec"])
            deltas.append(arrive - depart)
        median = float(pd.Series(deltas).median())
        expected = spacing_m / 1000.0 / float(speed) * 3600.0
        default_expected = spacing_m / 1000.0 / speed_default * 3600.0
        if abs(median - expected) > 2:
            errors.append(
                f"{route_id} travel {median:.1f}s on {spacing_m:.0f} m, "
                f"expected {expected:.1f}s at {speed} km/h"
            )
        if abs(median - default_expected) <= 2 and abs(expected - default_expected) > 2:
            errors.append(f"{route_id} still travels at the default {speed_default} km/h")

    if errors:
        print(f"{len(errors)} problem(s) in {gtfs_dir}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"OK: {city} feed in {gtfs_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
