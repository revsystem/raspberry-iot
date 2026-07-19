#!/usr/bin/env python3
"""DeviceList.csv の各デバイスからセンサデータを取得し、CSV と Prometheus textfile に出力する。

crontab (毎分実行):
* * * * * cd /home/pi/raspberry-sensor-collector; .venv/bin/python3 sensors_to_prometheus.py
"""

import configparser
import csv
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

from prometheus_client import CollectorRegistry, Gauge, write_to_textfile

import remo
import switchbot

BASE_DIR = Path(__file__).resolve().parent

# 開始時刻と、分単位に丸めた基準時刻 (30秒以上は切り上げ)
start_date = datetime.today()
master_date = start_date.replace(second=0, microsecond=0)
if start_date.second >= 30:
    master_date += timedelta(minutes=1)

cfg = configparser.ConfigParser()
cfg.read(BASE_DIR / 'config.ini', encoding='utf-8')

# センサメトリクス専用のレジストリ
# (デフォルトレジストリだと python_*/process_* が混入し、node_exporter 側の同名メトリクスと衝突する)
registry = CollectorRegistry()


def fetch_with_retry(fetch, device):
    """fetch() を最大 Retry 回試行して結果を返す。全て失敗したときは None。"""
    for i in range(int(device['Retry'])):
        try:
            return fetch()
        except Exception:
            logging.warning('retry to get data [loop: %d, date: %s, device: %s]',
                            i, master_date, device['DeviceName'], exc_info=True)
    return None


# Nature Remoの電力データ取得
def getdata_remo(device):
    value = fetch_with_retry(
        lambda: remo.get_electric_power_data(device['Token'], device['API_URL']), device)
    if value is None:
        logging.error('cannot get data [date: %s, device: %s]', master_date, device['DeviceName'])
        return None
    return {
        'DeviceName': device['DeviceName'],
        'Date_Master': master_date,
        'Date': datetime.today(),
        'CumulativeEnergy': float(value['CumulativeEnergy']),
        'Watt': int(value['Watt']),
        'RevCumulativeEnergy': float(value['RevCumulativeEnergy']),
    }


# SwitchBot Hub 2の温湿度データ取得
def getdata_switchbot_hub2(device):
    value = fetch_with_retry(
        lambda: switchbot.get_data(device['Token'], device['API_URL'], device['Secret']), device)
    if value is None:
        logging.error('cannot get data [date: %s, device: %s]', master_date, device['DeviceName'])
        return None
    return {
        'DeviceName': device['DeviceName'],
        'Date_Master': master_date,
        'Date': datetime.today(),
        'Temperature': float(value['temperature']),
        'Humidity': float(value['humidity']),
        'lightLevel': float(value['lightLevel']),
    }


# データのCSV出力 (デバイス別・日別ファイルに追記)
def output_csv(data, csvpath):
    out_dir = Path(csvpath) / data['DeviceName'] / str(master_date.year) / master_date.strftime('%Y%m')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{data['DeviceName']}_{master_date.strftime('%Y%m%d')}.csv"

    is_new_file = not out_path.exists()
    with open(out_path, 'a', encoding='utf-8') as f:
        writer = csv.DictWriter(f, data.keys())
        if is_new_file:
            writer.writeheader()
        writer.writerow(data)


# Gaugeに値をセットし、promファイルに出力
def output_prometheus(device_name, values):
    for suffix, value in values.items():
        Gauge(f'{device_name}_{suffix}', 'Gauge', registry=registry).set(value)
    write_to_textfile(cfg['Path']['PromOutPut'], registry)


def output_prometheus_remo(data):
    values = {
        'CumulativeEnergy': data['CumulativeEnergy'],
        'RevCumulativeEnergy': data['RevCumulativeEnergy'],
        'Watt': data['Watt'],
    }
    output_prometheus(data['DeviceName'], values)

    # 00:00 の場合のみ、その日の起点値として専用のpromデータを出力
    if master_date.strftime('%H%M') == '0000':
        output_prometheus(data['DeviceName'],
                          {f'{suffix}_0000': value for suffix, value in values.items()})


def output_prometheus_hub2(data):
    output_prometheus(data['DeviceName'], {
        'Temperature': data['Temperature'],
        'Humidity': data['Humidity'],
        'LightLevel': data['lightLevel'],
    })


# SensorType -> (データ取得関数, prom出力関数)
HANDLERS = {
    'Nature_Remo': (getdata_remo, output_prometheus_remo),
    'Switchbot_Hub2': (getdata_switchbot_hub2, output_prometheus_hub2),
}


def main():
    with open(BASE_DIR / 'DeviceList.csv', encoding='utf-8') as f:
        devices = list(csv.DictReader(f))

    log_name = f"sensor_log_{master_date.strftime('%Y%m%d')}.log"
    logging.basicConfig(filename=f"{cfg['Path']['LogOutput']}/{log_name}", level=logging.INFO)

    success_num = 0
    for device in devices:
        handler = HANDLERS.get(device['SensorType'])
        if handler is None:
            continue
        getdata, output_prom = handler

        data = getdata(device)
        if data is None:
            continue

        output_csv(data, cfg['Path']['CSVOutput'])
        output_prom(data)
        success_num += 1

    # ハートビート。全デバイス失敗時もファイルを必ず書き直すことで、
    # 取得できなかったデバイスのメトリクスがファイルに残り続ける(=凍った値が生きて見える)のを防ぐ
    Gauge('sensors_last_run_timestamp_seconds',
          'Unix time when the sensor collector last completed a run',
          registry=registry).set(time.time())
    write_to_textfile(cfg['Path']['PromOutPut'], registry)

    logging.info('[master_date: %s start_date: %s end_date: %s success: %s/%s]',
                 master_date, start_date, datetime.today(), success_num, len(devices))


if __name__ == '__main__':
    main()
