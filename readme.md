# Generación de GTFS desde shapes

Genera un feed GTFS sintético por frecuencias a partir de geometrías de rutas (shapes), usando parámetros de operación como velocidad de operación, distancia entre estaciones, tiempo dwell time en parada, intervalo de salida, etc.

## Características

- **Pipeline en 6 pasos:** agency, calendar, routes, shapes, stops, stop_times, frequencies y trips en notebooks ejecutables en orden.
- **Configuración centralizada** en un único `params.json` (ciudad, operadora, calendario, distancia entre paradas, velocidad, dwell, intervalo de paso).
- **Entrada:** GeoJSON de shapes de rutas por ciudad, requieren tener identificador único.
- **Salida estándar GTFS** lista para validadores y motores de planificación de viajes.
- **Paradas sintéticas** a distancia fija (metros) sobre cada shape.
- **Tiempos de viaje** calculados por velocidad comercial y tiempo de espera en parada.
- **Velocidad de operación** considera velocidad general como parámetro y se agrega dwell time en parada.

## Requisitos

- Python 3
- `pandas`, `geopandas`, `shapely`, `pyproj`, `numpy`

## Manual de aplicación

1. Colocar shapes en `1-scraping_ruta_directa/data/proc/{ciudad}.geojson` (p. ej. con `scraping_curl.ipynb`).
2. Editar `2-generation-files-simples/params.json` (ciudad, agency, calendar, stops, stop_times, frequencies).
2. Abrir los notebooks en `2-generation-files-simples/` y ejecutarlos **en orden 1 → 6** (directorio de trabajo: `2-generation-files-simples`).
4. El feed GTFS queda en `data/{ciudad}/gtfs-output/`.
5. Comprimir manualmente y validar en [Canonical GTFS Schedule Validator](https://gtfs-validator.mobilitydata.org)

## Descripción de archivos

| # | Notebook | Entrada | Salida |
|---|----------|---------|--------|
| 1 | agency_calendar | params | agency.txt, calendar.txt |
| 2 | routes-shapes | `.../proc/{ciudad}.geojson` | routes.txt, shapes.txt, routes_clean.geojson |
| 3 | stops | routes_clean.geojson | stops.txt, segments.geojson, stops.geojson |
| 4 | stop_times | segments.geojson | stop_times.txt |
| 5 | frequencies | stop_times.txt | frequencies.txt |
| 6 | trips | stop_times.txt, routes_clean.geojson | trips.txt |


## Formato de archivos de entrada

### Archivo de shapes de rutas

Extracto de archivo geojson de rutas de ciudad
| route_id 	| data.route.shortName                              	| type 	| geometry                                          	|
|----------	|---------------------------------------------------	|------	|---------------------------------------------------	|
| 11       	| Puerto Alegre - Candelario Garza Tampico          	| Bus  	| LINESTRING (-97.85316 22.21716, -97.85241 22.2... 	|
| 12       	| Tampico - Colonias - El Fuerte - Penal por Av.... 	| Bus  	| LINESTRING (-98.07474 22.43424, -98.07414 22.4... 	|

**Descripción de columnas**
- **route_id:** identificador corto único de rutas
- **data.route.shortName:** Nombre amigable de ruta
- **geometry:** Linestring con geometría de ruta
- **type:** tipo de ruta según estandar GTFS.


| Código 	| Nombre GTFS 	| Descripción                                          	|
|--------	|-------------	|------------------------------------------------------	|
| 0      	| Tram        	| Tranvía, tren ligero o Streetcar.                    	|
| 1      	| Subway      	| Metro o tren de alta capacidad (Subterráneo).        	|
| 2      	| Rail        	| Ferrocarril nacional o interurbano (ej. Tren Maya).  	|
| 3      	| Bus         	| Cualquier servicio de autobús urbano (el más común). 	|
| 4      	| Ferry       	| Transbordadores o barcos de pasajeros.               	|
| 5      	| Cable Tram  	| Tranvía de cable (estilo San Francisco).             	|
| 6      	| Aerial Lift 	| Teleféricos, Góndolas o Cablebús.                    	|
| 7      	| Funicular   	| Trenes para pendientes pronunciadas.                 	|
| 11     	| Trolleybus  	| Autobuses eléctricos con catenaria superior.         	|
| 12     	| Monorail    	| Monorriel.                                           	|



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


## TODO

- [ ] **Velocidad y headway por ruta:** parametrizar velocidad de operación y headway por ruta (en lugar de valores globales). Debería ser posible dar una lista de rutas y sus velocidades y headways y que el notebook `4-generation_stop_times.ipynb` lo consuma para generar la tabla `stop_times.txt` y `frequencies.txt`
- [ ] **Velocidad por zona:** hacer que la velocidad de operación dependa de la zona de la ciudad (p. ej. polígono o atributo espacial). Se debería poder asignar velocidad a vias primarias, secundarias y terciarias por zona de la ciudad (creo que ya hay una metodolo´gia para hacer esto, se iusó en la calculadora de accesibilidad usando la red nacional de caminos y datos de OSM). Y se debería considerar también la velocidad de la ruta reportada (si es que tiene).
- [ ] **Generación de varios horarios de operación:** horario de máxima demanda, horario valle, etc.
- [ ] **Posibilidad de usar paradas prestablecidas de rutas:** en caso de que se cuente con información de las paradas de las rutas de una o varias rutas, cargar las paradas para armar el GTFS.
- [ ] **Distancia entre paradas por ruta:** definir distancia entre paradas por rutas a partir de datos de entrada
