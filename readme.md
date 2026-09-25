# 🚍 GTFS Generation from Route Shapes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GTFS](https://img.shields.io/badge/GTFS-compliant-green.svg)](https://gtfs.mobilitydata.org/spec/gtfs-schedule)
[![Made with Jupyter](https://img.shields.io/badge/Made%20with-Jupyter-orange?logo=Jupyter)](https://jupyter.org/)

> Automated pipeline to generate synthetic GTFS feeds from public transit route geometries.

A [General Transit Feed Specification (GTFS) Schedule](https://gtfs.mobilitydata.org/spec/gtfs-schedule) generator for creating synthetic transit feeds from route geometries. This tool is used for mobility analysis and transport planning at **ITDP** (Institute for Transportation and Development Policy). 

**Generates two GTFS formats:**
- **GTFS with frequencies** — Uses `frequencies.txt` to define service headways (interval-based schedules)
- **GTFS with stop_times** — Uses explicit schedules in `stop_times.txt` (compatible with r5r/r5py)

The generated **synthetic GTFS** is designed to work with tools like **[r5r](https://ipeagit.github.io/r5r/)** for accessibility analysis, travel time calculations, and transport network evaluation. Note that this tool creates artificial transit schedules based on assumed parameters (speeds, frequencies, stop spacing) rather than real operational data.




## Features

- 🎯 **Automated stop generation** — Creates equidistant stops along route geometries
- ⚙️ **Configurable parameters** — Customize stop spacing, speeds, and frequencies per route
- ✅ **GTFS compliance** — Generates valid GTFS feeds compatible with standard validators
- 📝 **Flexible configuration** — Single JSON file to configure all parameters
- 🔍 **Validation built-in** — Automatic checks for data integrity and GTFS compliance


## How It Works

1. **Load route geometries** — Reads LineString geometries from input GeoJSON
2. **Generate equidistant stops** — Creates stops at fixed intervals (e.g., every 200m) along each route
3. **Assign speeds** — Each route gets a global default speed or a specific speed (km/h)
4. **Define frequencies** — Each route is assigned a departure frequency (headway in minutes)
5. **Calculate travel times** — Computes stop_times based on distance and speed
6. **Build GTFS** — Generates all required GTFS files (agency, routes, stops, shapes, stop_times, trips, frequencies, calendar)
7. **Validate** — Checks data integrity (ascending distances, no duplicate coordinates)


## Quick Start

1. **Install dependencies**
   ```bash
   pip install pandas geopandas shapely
   ```

2. **Prepare your data**
   - Edit `1-gtfs-generation/params.json` with your city configuration
   - Place route geometries in `data/{city}/routes-shapes/{city}.geojson` (see [Input Data Format](#input-data-format) below)

3. **Generate GTFS**
   - Run notebooks 1-7 sequentially in `1-gtfs-generation/`
   - Output: `data/{city}/gtfs_frequencies.zip`

3. **Optional: Generate stop times GTFS**
   - Install R dependencies:
     ```r
     install.packages("gtfstools")
     ```
   - Run notebook `8-convert_gtfs.ipynb` 
   - Output: `data/{city}/gtfs_stop_times.zip`

4. **Validate** → [MobilityData GTFS Validator](https://gtfs-validator.mobilitydata.org/)


## Configuration Parameters

All pipeline parameters are configured in a single JSON file: `params.json`

> 📋 **See a complete example:** Check `params-merida-city.json` for a real-world configuration example.

```json
{
  "city": "your_city_name",  // metadata
  "agency": {  // metadata
    "name": "Transit Agency Name",
    "id": "transit_agency_id",
    "url": "https://www.example-transit-agency.com",
    "timezone": "America/Mexico_City",
    "lang": "es"
  },
  "calendar": {  // metadata
    "start_date": "20260101",
    "end_date": "20261231",
    "SERVICE_ID": "weekday-service"
  },
  "stops": {
    "distance_between_stops": 200  // meters between stops
  },
  "stop_times": {
    "dwell_time_station_minutes": 0.2,  // time at each stop (0.2 = 12s)
    "speed_by_route": {  // km/h per route
      "Route A": 25.0,
      "Route B": 20.0,
      "Route C": 22.0,
      "default": 20.0
    }
  },
  "frequencies": {
    "headway_by_route": {  // minutes between departures
      "Route A": 10.0,
      "Route B": 15.0,
      "Route C": 12.0,
      "default": 15.0
    },
    "start_time": "06:00:00",  // begin time of trips
    "end_time": "22:00:00",  // end time of trips
    "exact_times": 1  // metadata
  }
}
```

**Note:** Parameters marked "GTFS metadata only" don't affect generation logic—only `distance_between_stops`, `dwell_time_station_minutes`, `speed_by_route`, and `headway_by_route` do.

## Input Data Format

This project uses a GeoJSON file as input data. The input file must be a **GeoJSON FeatureCollection** with **LineString geometries** representing transit routes. Place this file at: `data/{city}/routes-shapes/{city}.geojson`

> 📂 **Example data:** See `data/merida/` for a complete example of processed GTFS outputs, and `data/shapes_cities/` for example input route geometries.

**Required properties for each feature:**

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `route_name` | string | Full route name/identifier | `"Metrobus Linea 1"`, `"Metrobus Linea 2"` |
| `route_name_short` | string | Short route name for display | `"MB 1"`, `"MB 2"` |
| `route_type` | integer | GTFS route type ID (see table below) | `3` |
| `geometry` | LineString | Route geometry in any CRS | LineString coordinates |

**GTFS Route Type Reference:**

The `route_type` for each route should follow the [GTFS specification](https://gtfs.org/documentation/schedule/reference/#routestxt):

| ID | Type | Description |
|----|------|-------------|
| `0` | Tram, Streetcar, Light rail | Light rail or street level system within a metropolitan area |
| `1` | Subway, Metro | Underground rail system within a metropolitan area |
| `2` | Rail | Intercity or long-distance travel |
| `3` | Bus | Short- and long-distance bus routes |
| `4` | Ferry | Short- and long-distance boat service |
| `5` | Cable tram | Street-level rail cars where the cable runs beneath the vehicle |
| `6` | Aerial lift | Suspended cable car (gondola lift, aerial tramway) |
| `7` | Funicular | Rail system designed for steep inclines |
| `11` | Trolleybus | Electric buses that draw power from overhead wires |
| `12` | Monorail | Railway with a single rail or beam track |

**Notes:**
- Each LineString represents one route direction

## Next Steps

- [ ] **Distance between stops and dwell time by route** — Define distance between stops by routes from input data
- [ ] **Speed by zone** — Make operating speed depend on city zone (polygon or spatial attribute)
- [ ] **Multiple operation schedules** — Peak hours, off-peak hours, etc.
- [ ] **Predefined route stops** — Load existing stop information if available
- [ ] **Multiple routes per direction** — Support multiple routes in the same direction

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 

## Authors

**ITDP Mexico**
- Organization: [Institute for Transportation and Development Policy](https://www.itdp.org/)
- GitHub: [@ITDPmx](https://github.com/ITDPmx)



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
