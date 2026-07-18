# raspberry-iot

Gather variable data and visualized with Raspberry Pi.
These Ansible tasks are based on [Inkbirdの温湿度計のデータをRaspberry Piで取得しPrometheusとGrafanaで可視化する](https://qiita.com/revsystem/items/4097d0ff447913e2675a)
(Gathering data from Inkbird's thermo-hygrometer with Raspberry Pi and visualize it with Prometheus and Grafana.)

The sensor collector application (`roles/inkbird_ibsth/files/sensors_to_prometheus.py`) now gathers
data from Nature Remo (smart meter power) and SwitchBot Hub 2 (temperature/humidity/light) cloud APIs
instead of reading Inkbird IBS-TH1/TH2 sensors directly over Bluetooth. Bluetooth/Inkbird support has
been fully retired: the original BLE-based Inkbird code, the `bluetooth` service, and the native
libraries it needed (`bluez`, `libglib2.0-dev`, `libatlas-base-dev`) are no longer part of this
playbook.

## Requirements

- Ansible >= 11.3.0
- ansible-core >= 2.18.3

The `inkbird_ibsth` role installs [uv](https://docs.astral.sh/uv/) on the target host and runs
`uv sync` to build the sensor collector's virtual environment (`{inkbird_home}/.venv`), so the
target host needs outbound internet access during provisioning.

## Variables

### hosts

Fill in the ansible_host, ansible_user following your host.

```script:hosts
[IoT]
raspberry-iot ansible_host=192.168.1.100 ansible_user=pi
```

### Role Variables

| Name           | Path          | Default Value | Description          |
| -------------- | ------------- |-------------- |--------------------- |
| `grafana_version` | roles/grafana/defaults/main.yml | latest | Grafana package version |
| `influxdb_version` | roles/influxdb/defaults/main.yml | latest | Influxdb package version |
| `influxdb_hostname` | roles/influxdb/defaults/main.yml | localhost | Influxdb Hostname |
| `influxdb_database_name` | roles/influxdb/defaults/main.yml | prometheus | Influxdb DB name |
| `inkbird_home` | roles/inkbird_ibsth/defaults/main.yml | /home/pi/raspberry-inkbird_ibsth | Path to the sensor collector application directory |
| `prometheus_version` | roles/prometheus/defaults/main.yml | latest| Prometheus package version |
| `prometheus_hostname` | roles/prometheus/defaults/main.yml | localhost | Prometheus Host name |

### DeviceList.csv

CSV structure

| Name           | Description          |
| -------------- |--------------------- |
| DeviceName | Manage device name. Using as identifier |
| SensorType | Sensor class. `Nature_Remo` or `Switchbot_Hub2` are handled by `sensors_to_prometheus.py`; other values are skipped |
| MacAddress | Unused. Left over from the retired Bluetooth-based Inkbird schema; safe to leave blank |
| Timeout | Value of timeout when scanning |
| Retry | Max number of retry |
| Offset_Temp | Unused by the current sensor types |
| Offset_Humid | Unused by the current sensor types |
| API_URL | Cloud API endpoint for the device (Nature Remo base URL, or SwitchBot device status URL) |
| Token | API access token/key |
| Secret | API signing secret (SwitchBot only; empty for Nature Remo) |

`roles/inkbird_ibsth/files/DeviceList.csv` in this repository only contains placeholder rows. It
holds real API tokens/secrets in production, so replace it with your own file (or override its
content per-host) rather than committing real credentials.

## Usage

```bash
ansible-playbook -i hosts -b iot.yml --diff  --check
ansible-playbook -i hosts -b iot.yml --diff
```

You need to setup the Grafana dashboard.

- login with Admin account.
- connect to the datasource. ( InfluxDB )
- create the dashborad using datasource.
- add panels as you like.

## Licensing

Ansible role for grafana was borrowed from the fine work done by the [cloudalchemy group](https://github.com/cloudalchemy/ansible-grafana), thanks you.

Their code is licensed under an [MIT style license](https://github.com/cloudalchemy/ansible-grafana/blob/master/LICENSE).

> Copyright (c) 2017-2018 Pawel Krupa, Roman Demachkovych
>
> Permission is hereby granted, free of charge, to any person obtaining a > copy
> of this software and associated documentation files (the "Software"), to > deal
> in the Software without restriction, including without limitation the > rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in > all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING > FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN > THE
> SOFTWARE.

This project originally read Inkbird IBS-TH1 sensors over Bluetooth using Python code borrowed from
[家の中のセンサデータをRaspberryPiで取得しまくり、スーパーIoTハウスを実現 (@c60evaporator)](https://qiita.com/c60evaporator/items/283d0569eba58830f86e).
That code has since been removed along with the rest of the Bluetooth/Inkbird support (see above).
