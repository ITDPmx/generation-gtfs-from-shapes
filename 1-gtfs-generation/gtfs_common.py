"""Shared helpers for the synthetic GTFS notebooks."""

from __future__ import annotations

import geopandas as gpd
import pandas as pd
from pyproj import CRS

TRIP_SUFFIX = "_trip_00"


def shape_id_for(route_id: str) -> str:
    return f"Shape_{route_id}"


def trip_id_for(route_id: str) -> str:
    return f"{route_id}{TRIP_SUFFIX}"


def route_id_from_trip_id(trip_id: str) -> str:
    text = str(trip_id)
    if text.endswith(TRIP_SUFFIX):
        return text[: -len(TRIP_SUFFIX)]
    return text


def utm_crs_from_centroid(gdf: gpd.GeoDataFrame) -> CRS:
    """UTM CRS of the layer centroid, after transforming to WGS84."""
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS.")
    g4326 = gdf.to_crs(4326)
    if hasattr(g4326, "union_all"):
        geom = g4326.union_all()
    else:
        geom = g4326.unary_union
    lon, lat = float(geom.centroid.x), float(geom.centroid.y)
    zone = int((lon + 180) // 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)


def to_local_utm(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject to the UTM zone of the centroid (via WGS84)."""
    return gdf.to_crs(utm_crs_from_centroid(gdf))


def resolve_route_param(route_id, route_short_name, table: dict):
    """Return (value, matched_key) or (None, None).

    Match order: exact route_id, exact route_short_name, then case-insensitive
    match on either. The ``default`` key is not a route match.
    """
    if not isinstance(table, dict):
        return None, None

    candidates = (str(route_id), str(route_short_name))
    for key in candidates:
        if key in table and key != "default":
            return table[key], key

    folded = {}
    for key, value in table.items():
        if key == "default":
            continue
        folded.setdefault(str(key).casefold(), (key, value))
    for key in candidates:
        hit = folded.get(key.casefold())
        if hit is not None:
            return hit[1], hit[0]
    return None, None


def map_route_params(
    routes_df: pd.DataFrame,
    table: dict,
    default,
    kind: str,
) -> dict:
    """Map each route_id to a parameter value.

    Prints the routes that matched a configured key, unused keys, and how many
    routes fell back to ``default``.
    """
    values = {}
    matched_keys = set()
    defaulted = []
    for row in routes_df.itertuples(index=False):
        value, key = resolve_route_param(row.route_id, row.route_short_name, table)
        if key is None:
            values[row.route_id] = default
            defaulted.append(row.route_id)
        else:
            values[row.route_id] = value
            matched_keys.add(key)
            print(f"{kind}: {key!r} -> {row.route_id} = {value}")

    matched_folded = {str(key).casefold() for key in matched_keys}
    unused = [
        key
        for key in table
        if key != "default" and str(key).casefold() not in matched_folded
    ]
    if unused:
        print(f"Warning: {kind} keys not matched to any route: {unused}")
    if defaulted:
        print(f"{kind}: {len(defaulted)} route(s) use default {default}")
    return values
