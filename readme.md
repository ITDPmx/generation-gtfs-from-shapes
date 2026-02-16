# Generacion GTFS ITDP

Repositorio del **ITDP (Instituto de Politicas para el Transporte y el Desarrollo)** para construir datasets GTFS a partir de geometrias de rutas y supuestos operativos.

## Resumen de producto

Este proyecto convierte datos base de rutas urbanas en entregables GTFS utiles para:

- analisis de accesibilidad y cobertura
- simulacion de escenarios de servicio
- interoperabilidad con herramientas de planeacion y analitica de movilidad
- publicacion de insumos estandarizados para equipos tecnicos

En terminos de producto, este repo habilita un flujo de "datos crudos de rutas -> GTFS estatico -> GTFS con `frequencies.txt`".

## Problema que resuelve

Muchas ciudades no cuentan con GTFS oficial, o lo tienen incompleto/desactualizado. Este flujo permite:

- estructurar rutas en formato estandar GTFS
- generar `trips.txt` y `stop_times.txt` cuando no existe programacion detallada
- producir una variante basada en frecuencias para analisis de planeacion

## Estado actual (corte: 2026-02-16)

- Cobertura de scraping: **23 ciudades** en `1-scraping_ruta_directa/data/proc/`.
- Ciudades con pipeline de generacion trabajado en este repo: **Tampico** y **Guadalajara**.
- Motor central de conversion GTFS en Python: `4-make_gtfs/`.
- Flujo operativo actual: mayormente basado en notebooks (prototipo + operacion asistida).

Metricas de artefactos existentes:

| Ciudad | Etapa | Rutas/Frequencies | Trips | Stop times | Stops |
|---|---|---:|---:|---:|---:|
| Tampico | `4-make_gtfs/data/tampico` | 121 rutas | 3025 | 134425 | 1459 |
| Guadalajara | `4-make_gtfs/data/guadalajara` | 254 rutas | 3810 | 30000 | 455 |
| Tampico (freq) | `5-conversion-trips-to-frequency/data/export_gtfs/tampico_modified_gtfs` | 121 frequencies | 121 | 20804 | 20804 |
| Guadalajara (freq) | `5-conversion-trips-to-frequency/data/export_gtfs/guadalajara_modified_gtfs` | 254 frequencies | 254 | 54258 | 54258 |

## Arquitectura del producto (pipeline en 5 etapas)

| Etapa | Carpeta | Objetivo de producto | Salida principal |
|---|---|---|---|
| 1 | `1-scraping_ruta_directa/` | Extraer rutas desde Ruta Directa | GeoJSON por ciudad |
| 2 | `2-fix-routes-ruta-directa/` | Limpiar y normalizar trazos por ruta | Rutas individuales/depuradas |
| 3 | `3-generacion-archivos-make_gtfs/` | Construir insumos para `make_gtfs` | `meta.csv`, `service_windows.csv`, `frequencies.csv`, `shapes.geojson`, `speed_zones.geojson`, opcional `stops.csv` |
| 4 | `4-make_gtfs/` | Generar GTFS estatico | `agency.txt`, `calendar.txt`, `routes.txt`, `shapes.txt`, `stops.txt`, `trips.txt`, `stop_times.txt` |
| 5 | `5-conversion-trips-to-frequency/` | Rearmar GTFS orientado a frecuencias | `frequencies.txt` + `trips.txt` + `stop_times.txt` + empaquetado ZIP |

## Entradas y salidas clave

### Entradas minimas para `make_gtfs`

En una carpeta fuente (ejemplo: `3-generacion-archivos-make_gtfs/data/proc/tampico`):

- `meta.csv`
- `service_windows.csv`
- `frequencies.csv`
- `shapes.geojson`

Opcionales:

- `speed_zones.geojson`
- `stops.csv`

### Salidas GTFS estandar

`make_gtfs` produce:

- `agency.txt`
- `calendar.txt`
- `routes.txt`
- `shapes.txt`
- `stops.txt`
- `trips.txt`
- `stop_times.txt`

## Guia rapida de operacion

### 1) Generar GTFS estatico (motor principal)

```bash
cd 4-make_gtfs
uv run make_gtfs ../3-generacion-archivos-make_gtfs/data/proc/tampico ./data/tampico
```

Para exportar directo a ZIP:

```bash
cd 4-make_gtfs
uv run make_gtfs ../3-generacion-archivos-make_gtfs/data/proc/tampico ./data/tampico/gtfs.zip
```

### 2) Ejecutar pruebas del motor (recomendado)

```bash
cd 4-make_gtfs
uv run pytest
```

## Supuestos y limitaciones actuales

Para gestion de producto y calidad de datos, considera:

- El pipeline completo no esta orquestado como un solo comando; depende de notebooks.
- Hay rutas/paths hardcodeados en notebooks que deben ajustarse por ciudad.
- En `3-generacion-archivos-make_gtfs/data/proc/*/meta.csv` aparece timezone plantilla (`Pacific/Auckland`) que luego se corrige en etapa 5.
- `frequencies.csv` de Tampico y Guadalajara usa `route_type=2` en los artefactos actuales; revisar alineacion con clasificacion modal objetivo.
- La etapa de conversion a frecuencias tiene salidas heterogeneas por ciudad (por ejemplo, empaquetado final completo en Tampico y parcial en Guadalajara).

## Requisitos tecnicos

- Python 3.10+
- `uv` para manejo de entorno/dependencias
- Librerias geoespaciales (via `4-make_gtfs/pyproject.toml`): `geopandas`, `shapely`, `gtfs-kit`, `pandera`, etc.
- Jupyter para ejecutar notebooks de etapas 1, 2, 3 y 5

## Estructura del repositorio

```text
generacion-gtfs/
├── 1-scraping_ruta_directa/
├── 2-fix-routes-ruta-directa/
├── 3-generacion-archivos-make_gtfs/
├── 4-make_gtfs/
├── 5-conversion-trips-to-frequency/
├── utils/
└── old/
```

## Roadmap sugerido (producto)

1. Pasar de notebooks a pipeline reproducible por CLI (por ciudad).
2. Estandarizar parametros por ciudad (timezone, route_type, headways, ventanas de servicio).
3. Agregar validacion automatica end-to-end de GTFS por etapa.
4. Versionar entregables GTFS por ciudad y fecha de corte.
5. Definir criterios de calidad de producto (completitud, consistencia espacial, consistencia temporal).

## Referencias internas

- Motor GTFS: `4-make_gtfs/README.rst`
- Codigo principal: `4-make_gtfs/make_gtfs/`
- Pruebas: `4-make_gtfs/tests/`
