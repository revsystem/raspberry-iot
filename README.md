# raspberry-iot

Gather variable data and visualized with Raspberry Pi.
These Ansible tasks are based on [Inkbirdの温湿度計のデータをRaspberry Piで取得しPrometheusとGrafanaで可視化する](https://qiita.com/revsystem/items/4097d0ff447913e2675a)
(Gathering data from Inkbird's thermo-hygrometer with Raspberry Pi and visualize it with Prometheus and Grafana.)

## Requirements

- Ansible >= 2.7

## Variables

### ssh.confg

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
| `inkbird_home` | roles/inkbird_ibsth/defaults/main.yml | /home/pi/raspberry-inkbird_ibsth | Path to Inkbird home directory |
| `prometheus_version` | roles/prometheus/defaults/main.yml | latest| Prometheus package version |
| `prometheus_hostname` | roles/prometheus/defaults/main.yml | localhost | Prometheus Host name |

### DeviceList.csv

CSV structure
| Name           | Description          |
| -------------- |--------------------- |
| DeviceName | Manage device name. Using as identifier |
| SensorType | kind of sensors. Using for getting sensor class |
| MacAddress | MacAddress of sensors |
| Timeout | Value of timeout when scanning |
| Retry | Max number of retry |

Specification.

- [設定ファイル](https://qiita.com/c60evaporator/items/283d0569eba58830f86e#%E8%A8%AD%E5%AE%9A%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB)

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

Python code for Inkbird IBS-TH1 was borrowed by [家の中のセンサデータをRaspberryPiで取得しまくり、スーパーIoTハウスを実現 (@c60evaporator)](https://qiita.com/c60evaporator/items/283d0569eba58830f86e)
