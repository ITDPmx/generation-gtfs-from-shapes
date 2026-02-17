# Generación de GTFS desde shapes

Genera un feed GTFS por frecuencias a partir de geometrías de rutas (shapes), por ejemplo scrapeadas de Ruta Directa.

## Características

- **Pipeline en 6 pasos:** agency, calendar, routes, shapes, stops, stop_times, frequencies y trips en notebooks ejecutables en orden.
- **Configuración centralizada** en un único `params.json` (ciudad, operadora, calendario, distancia entre paradas, velocidad, dwell, intervalo de paso).
- **Entrada:** GeoJSON de shapes por ciudad (p. ej. `1-scraping_ruta_directa/data/proc/{ciudad}.geojson`).
- **Salida estándar GTFS** lista para validadores y motores de planificación de viajes.
- **Paradas sintéticas** a distancia fija (metros) sobre cada shape.
- **Tiempos de viaje** calculados por velocidad comercial y tiempo de espera en parada; frecuencias por ventana horaria e intervalo.

## Requisitos

- Python 3
- `pandas`, `geopandas`, `shapely`, `pyproj`, `numpy`

## Uso rápido

1. Disponer de shapes en `1-scraping_ruta_directa/data/proc/{ciudad}.geojson` (p. ej. con `scraping_curl.ipynb`).
2. Editar `2-generation-files-simples/params.json` (ciudad, agency, calendar, stops, stop_times, frequencies).
3. Abrir los notebooks en `2-generation-files-simples/` y ejecutarlos **en orden 1 → 6** (directorio de trabajo: `2-generation-files-simples`).
4. El feed GTFS queda en `data/{ciudad}/gtfs-output/`.

## Estructura del proyecto

```
generation-gtfs-from-shapes-v2/
├── 1-scraping_ruta_directa/data/proc/   # Entrada: {ciudad}.geojson (shapes crudos)
├── 2-generation-files-simples/          # Notebooks 1–6 + params.json
└── data/{ciudad}/
    ├── gtfs-output/    # agency, calendar, routes, shapes, stops, stop_times, frequencies, trips
    └── processed/      # routes_clean.geojson, segments.geojson, stops.geojson (intermedios)
```

## Pipeline (notebooks)

| # | Notebook | Entrada | Salida |
|---|----------|---------|--------|
| 1 | agency_calendar | params | agency.txt, calendar.txt |
| 2 | routes-shapes | `.../proc/{ciudad}.geojson` | routes.txt, shapes.txt, routes_clean.geojson |
| 3 | stops | routes_clean.geojson | stops.txt, segments.geojson, stops.geojson |
| 4 | stop_times | segments.geojson | stop_times.txt |
| 5 | frequencies | stop_times.txt | frequencies.txt |
| 6 | trips | stop_times.txt, routes_clean.geojson | trips.txt |

## Configuración (params.json)

Archivo: `2-generation-files-simples/params.json`.

```json
{
  "ciudad": "tampico",
  "agency": {
    "name": "Red de Transporte Tampico",
    "id": "IMEPLAN_Tampico",
    "url": "http://www.imeplansurdetamaulipas.gob.mx",
    "timezone": "America/Mexico_City",
    "lang": "es"
  },
  "calendar": {
    "start_date": "20260101",
    "end_date": "20260102",
    "service_id_valle": "L_V_VALLE",
    "service_id_pico": "L_V_PICO",
    "service_id_finde": "S_D"
  },
  "stops": {
    "distancia_entre_estaciones": 200
  },
  "stop_times": {
    "dwell_time_station_minutes": 0.2,
    "velocidad_kmh": 28.13
  },
  "frequencies": {
    "intervalo_minutos": 13.11,
    "start_time": "06:00:00",
    "end_time": "07:00:00",
    "exact_times": 1
  }
}
```

- **ciudad**: carpeta en `data/` y nombre del GeoJSON en `1-scraping.../proc/`.
- **agency** / **calendar** → agency.txt, calendar.txt y trips.
- **stops**, **stop_times**, **frequencies** → notebooks 3, 4 y 5.

Especificación de tablas GTFS: `files_gtfs_to_generate.md`.

## TODO

- [ ] **Velocidad y headway por ruta:** parametrizar velocidad de operación y headway por ruta (en lugar de valores globales).
- [ ] **Velocidad por zona:** hacer que la velocidad dependa de la zona de la ciudad (p. ej. polígono o atributo espacial).
