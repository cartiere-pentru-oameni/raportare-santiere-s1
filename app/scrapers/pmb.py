"""
Scrape Sector 1 building permits from PMB website (urbanism.pmb.ro)
"""

import requests
import time

MAP_URL = "https://urbanism.pmb.ro/xportalurb/map/getfeature"
TABLE_URL = "https://urbanism.pmb.ro/xportalurb/EntityList/GetData"

HEADERS = {
    'sec-ch-ua-platform': '"Linux"',
    'Referer': 'https://urbanism.pmb.ro/xportalurb/Map/MapRun?idMap=2&idApp=6',
    'x-app': '6',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'sec-ch-ua': '"Brave";v="143", "Chromium";v="143"',
    'sec-ch-ua-mobile': '?0',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/json',
}

BUCHAREST_BBOX = {
    'min_x': 573000,
    'max_x': 602000,
    'min_y': 314000,
    'max_y': 340000
}


def _fetch_table_data():
    """Fetch all building permits from table API"""
    print("[PMB] Fetching permits from table API...")
    all_permits = []
    skip = 0
    page_size = 5000

    while True:
        page_num = (skip // page_size) + 1

        params = {
            'take': page_size,
            'skip': skip,
            'page': page_num,
            'pageSize': page_size,
            'id': 5,
            'filters': '{"fld_61":""}'
        }

        try:
            response = requests.get(TABLE_URL, params=params, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()

            permits = data.get('Data', [])
            total = data.get('Total', 0)

            print(f"[PMB]   Page {page_num}: got {len(permits)} permits (total available: {total})")

            if not permits:
                break

            all_permits.extend(permits)

            if skip + page_size >= total:
                break

            skip += page_size
            time.sleep(0.5)

        except Exception:
            break

    print(f"[PMB] Table API: fetched {len(all_permits)} permits total")
    return all_permits


def _fetch_map_data():
    """Fetch permit coordinates from map API"""
    print("[PMB] Fetching coordinates from map API...")
    bbox_str = f"{BUCHAREST_BBOX['min_x']},{BUCHAREST_BBOX['min_y']},{BUCHAREST_BBOX['max_x']},{BUCHAREST_BBOX['max_y']},EPSG:3844"

    params = {
        'layer': 11,
        'srs': 'EPSG:3844',
        'bbox': bbox_str,
        'idMap': 2
    }

    try:
        response = requests.get(MAP_URL, params=params, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()

        features = data.get('features', [])
        map_by_id = {}
        for feature in features:
            feature_id = str(feature.get('id'))
            map_by_id[feature_id] = feature

        print(f"[PMB] Map API: fetched {len(map_by_id)} coordinates")
        return map_by_id

    except Exception:
        print("[PMB] Map API: failed to fetch coordinates")
        return {}


def _filter_sector1(table_permits, map_data):
    """Filter for Sector 1 and merge with map data"""
    sector1_permits = []

    for permit in table_permits:
        sector = str(permit.get('fld_57', '')).strip()

        if sector == '1':
            permit_id = str(permit['id'])
            map_feature = map_data.get(permit_id)

            # Build address
            street_type = (permit.get('fld_48_fktext') or '').strip()
            street = (permit.get('fld_55') or '').strip()
            number = (permit.get('fld_56') or '').strip()
            sector_val = (permit.get('fld_57') or '').strip()

            address_parts = []
            if street_type:
                address_parts.append(street_type)
            if street:
                address_parts.append(street)
            if number:
                address_parts.append(f"nr {number}")
            if sector_val:
                address_parts.append(f"sector {sector_val}")

            address = ", ".join(address_parts) if address_parts else "N/A"

            # Build data dictionary
            data_dict = {
                "ID": str(permit.get('id', '')),
                "Permit Number": str(permit.get('fld_46', '')),
                "Date": str(permit.get('fld_47', '')),
                "Street Type": str(permit.get('fld_48_fktext', '')),
                "Street": str(permit.get('fld_55', '')),
                "Number": str(permit.get('fld_56', '')),
                "Sector": str(permit.get('fld_57', '')),
                "Beneficiary": str(permit.get('fld_64', '')),
                "Description": str(permit.get('fld_58', '')),
                "Cadastral": str(permit.get('fld_65', '')),
                "CU Number": str(permit.get('fld_63', '')),
            }

            # Add map data if available
            if map_feature:
                map_props = map_feature.get('properties', {})
                geometry = map_feature.get('geometry', {})
                coords_list = geometry.get('coordinates', [])

                if coords_list and isinstance(coords_list, list) and len(coords_list) > 0:
                    coords = coords_list[0]
                    if isinstance(coords, list) and len(coords) == 2:
                        data_dict["Coordinates X"] = str(coords[0])
                        data_dict["Coordinates Y"] = str(coords[1])

                if map_props.get('nr_ac'):
                    data_dict["AC Number"] = str(map_props.get('nr_ac', ''))
                if map_props.get('valoare'):
                    data_dict["Value"] = str(map_props.get('valoare', ''))
                if map_props.get('exec_valab'):
                    data_dict["Execution Validity"] = str(map_props.get('exec_valab', ''))
                if map_props.get('functiune'):
                    data_dict["Function"] = str(map_props.get('functiune', ''))

            permit_obj = {
                "address": address,
                "data": data_dict,
                "source": {
                    "issuer": "pmb",
                    "url": "https://urbanism.pmb.ro/xportalurb/Map/MapRun?idMap=2&idApp=6"
                }
            }

            sector1_permits.append(permit_obj)

    # Sort by date (newest first)
    sector1_permits.sort(key=lambda x: x['data'].get('Date', ''), reverse=True)

    return sector1_permits


def scrape_permits():
    """
    Scrape Sector 1 building permits from PMB.
    Returns list of permit dictionaries.
    """
    print("[PMB] Starting PMB scraper...")
    table_permits = _fetch_table_data()

    if not table_permits:
        raise Exception("No permits fetched from PMB table API")

    map_data = _fetch_map_data()

    print("[PMB] Filtering Sector 1 permits...")
    sector1_permits = _filter_sector1(table_permits, map_data)

    print(f"[PMB] Done! Found {len(sector1_permits)} Sector 1 permits")
    return sector1_permits
