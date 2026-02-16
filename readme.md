# Generación de GTFS desde shapes

Genera un feed GTFS por frecuencias a partir de geometrías de rutas (p. ej. scrapeadas de Ruta Directa). Parámetros en `2-generation-files-simples/params.json`. Ejecutar los notebooks **1 → 6** en orden, con el directorio de trabajo en `2-generation-files-simples`.

**Requisitos:** `pandas`, `geopandas`, `shapely`, `pyproj`, `numpy`.

---

## Estructura y datos

```
generation-gtfs-from-shapes-v2/
├── 1-scraping_ruta_directa/data/proc/   # Entrada: {ciudad}.geojson (shapes crudos)
├── 2-generation-files-simples/          # Notebooks 1–6 + params.json
└── data/{ciudad}/
    ├── gtfs-output/    # GTFS final: agency, calendar, routes, shapes, stops, stop_times, frequencies, trips
    └── processed/      # Intermedios: routes_clean.geojson, segments.geojson, stops.geojson
```

---

## Notebooks (orden 1 → 6)

| # | Notebook | Entrada | Salida |
|---|----------|---------|--------|
| 1 | agency_calendar | params | agency.txt, calendar.txt |
| 2 | routes-shapes | `1-scraping.../proc/{ciudad}.geojson` | routes.txt, shapes.txt, routes_clean.geojson |
| 3 | stops | routes_clean.geojson + distancia_entre_estaciones | stops.txt, segments.geojson, stops.geojson |
| 4 | stop_times | segments.geojson + velocidad/dwell | stop_times.txt |
| 5 | frequencies | stop_times.txt + intervalo/ventana horaria | frequencies.txt |
| 6 | trips | stop_times.txt, routes_clean.geojson + service_id | trips.txt |

---

## params.json

Diccionario de configuración (ruta: `2-generation-files-simples/params.json`):

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
- **agency** → agency.txt y referencias. **calendar** → calendar.txt y trips.
- **stops.distancia_entre_estaciones** (m) → notebook 3. **stop_times** → notebook 4. **frequencies** → notebook 5.

Especificación de tablas GTFS: `files_gtfs_to_generate.md`.

---

## TODO

- **Velocidad y headway por ruta:** parametrizar velocidad de operación y headway (intervalo de paso) por ruta en lugar de valores únicos globales.
- **Velocidad por zona:** hacer que la velocidad dependa de la zona de la ciudad (p. ej. por polígono o atributo espacial) para reflejar condiciones locales.
