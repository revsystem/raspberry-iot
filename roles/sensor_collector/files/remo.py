"""Nature Remo Cloud API からスマートメータの電力データを取得する。"""

import requests

TIMEOUT = 10  # seconds


def get_electric_power_data(token: str, api_url: str) -> dict | None:
    """電力データを取得して dict で返す。スマートメータが見つからないときは None。"""
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'{api_url}/1/appliances', headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    return _decode_smart_meter_data(response.json())


def _decode_smart_meter_data(appliances: list[dict]) -> dict | None:
    value: dict = {}
    coefficient = 1
    energy_unit = 1.0

    for appliance in appliances:
        if appliance['type'] != 'EL_SMART_METER':
            continue
        properties = appliance['smart_meter']['echonetlite_properties']

        # 積算量を実データに換算するための係数と、積算電力量の単位
        for prop in properties:
            if prop['name'] == 'coefficient':
                coefficient = int(prop['val'])
            elif prop['name'] == 'cumulative_electric_energy_unit':
                if int(prop['val']) == 1:
                    energy_unit = 0.1
                elif int(prop['val']) == 2:
                    energy_unit = 0.01

        # スマートメータの電力データ
        for prop in properties:
            if prop['name'] == 'normal_direction_cumulative_electric_energy':
                value['CumulativeEnergy'] = float(prop['val']) * coefficient * energy_unit
            elif prop['name'] == 'reverse_direction_cumulative_electric_energy':
                value['RevCumulativeEnergy'] = float(prop['val']) * coefficient * energy_unit
            elif prop['name'] == 'measured_instantaneous':
                value['Watt'] = int(prop['val'])

    return value or None
