"""DeviceList.csv に登録された SwitchBot デバイスへの疎通確認スクリプト。"""

import csv
from pathlib import Path

import switchbot

if __name__ == '__main__':
    with open(Path(__file__).resolve().parent / 'DeviceList.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['SensorType'] != 'Switchbot_Hub2':
                continue
            data = switchbot.get_data(row['Token'], row['API_URL'], row['Secret'])
            print(f"{row['DeviceName']}: {data}")
