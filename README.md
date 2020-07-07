# energy-trading-platform

[![Build Status](https://travis-ci.org/NCKU-CCS/energy-trading-platform.svg?branch=cswang%2Fet_platform)](https://travis-ci.org/NCKU-CCS/energy-trading-platform)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform?ref=badge_shield)

[![Maintainability](https://api.codeclimate.com/v1/badges/71f39cd72ca8e5eac1ec/maintainability)](https://codeclimate.com/github/NCKU-CCS/energy-trading-platform/maintainability)

[![Coverage Status](https://coveralls.io/repos/github/NCKU-CCS/energy-trading-platform/badge.svg?branch=develop)](https://coveralls.io/github/NCKU-CCS/energy-trading-platform?branch=develop)

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform?ref=badge_shield)


主要功能為綠能交易平台的 API，詳細資訊：[API Document](https://et01.docs.apiary.io/#)

## Getting Started

### Prerequisites

- python 3.6.8
- docker 19.03.5


### Running Development

Installing Packages & Running
```
pipenv install
pipenv run python pt/app.py
```

### Running Production

1. update the .env file
2. run docker
```
docker build -t et_platform . --no-cache
docker run --env-file .env --name et_platform -d -p 5000:5000 --restart=always et_platform
```

### Database

Database using UTC timezone to store timestamps.

Through the setting at [base_models](./pt/utils/base_models.py), ORM will convert UTC time to local time when reading and searching data, and also convert local time to UTC time when saving data.

Some tables like `AMI` and `History` are saving and using in UTC timezone, because their timestamp data type is `Date`.

Most query can just use local time, we have known that few query way need to change to UTC time by your self, like `extract`.

+ Running database at background

    `docker-compose up -d`

### IOTA Tracker

+ Get Datas from IOTA and decrypt, based on address from database and tags from configs.

    `pipenv run python pt/iota_tracker.py`

#### Run with Crontab

+ Run IOTA Tracker every minutes and save logs

    `* * * * * cd /home/user/energy-trading-platform && /usr/local/bin/pipenv run python pt/scripts/iota_tracker.py >> /home/user/et_logs/`date +\%Y-\%m-\%d`.log 2>&1`

*Crontab doesn't know PATH at runtime, direct use pipenv's binary file to execute.

## [GET] address

+ 提供 AMI Data Uploader 詢問上傳的 IOTA Address

+ Authorization: Bearer Token

+ Address 規則：
    + 每個上傳 AMI 對應到一個 Address
    + 每天更新一次 Address

## Simulate Data

- 模擬資料傳送至平台

### Powerdata

- 模擬 BEMS 的 用電資料傳送至平台

```bash
sh /energy-trading-platform-simulate/pt/simulate/trigger/data.sh <bems_name> <simulate_data_path>
```

#### Description

| Name               | Description                                           |
|--------------------|-------------------------------------------------------|
| bems_name          | BEMS account name                                     |
| simulate_data_path | .csv file path. The .csv file must in specific format |
|                    |                                                       |

#### Powerdata Crontab Example

```bash
*/15 * * * * sh $HOME/energy-trading-platform/pt/simulate/trigger/data.sh ABC_BEMS $HOME/ABC_BEMS.csv
```

#### Powerdata Data Example

ABRI_BEMS

```csv
AMI_1,AMI_2,AMI_3,total_load(kW),PV_generate(kW),net_load(kW),TIME
8,12.16,1.8,21.96,0,21.96,2020/5/2 00:00
8.5,10.88,2.2,21.58,0,21.58,2020/5/2 00:15
8.5,11.52,1.6,21.62,0,21.62,2020/5/2 00:30
```

Carlab_BEMS

```csv
id,field,grid_power,inserted_at
4451,carlab,12.228,2020/4/25 00:00
4452,carlab,11.817,2020/4/25 00:15
4453,carlab,12.13,2020/4/25 00:30
4454,carlab,12.264,2020/4/25 00:45
4455,carlab,12.069,2020/4/25 01:00
```

NCKU_BEMS

```csv
id,field,grid_power,inserted_at
33147,NCKU,1.075,2020/3/14 00:00
33148,NCKU,1.087,2020/3/14 00:15
33149,NCKU,1.072,2020/3/14 00:30
33150,NCKU,1.067,2020/3/14 00:45
33151,NCKU,1.073,2020/3/14 01:00
```

### Bidsubmit

- 模擬 BEMS 的投標資料（買 or 賣）傳送至平台

```bash
sh /energy-trading-platform-simulate/pt/simulate/trigger/bidsubmit.sh <bems_account> <password> <bid_amount> <bid_value> <bid_type>
```

#### Bidsubmit Crontab Example

```bash
10 16 * * * sh $HOME/energy-trading-platform/pt/simulate/trigger/bidsubmit.sh ABC_BEMS password 10 20 buy
```

## Notice

+ set Time Zone at `.env` file

+ `.travis.yml` 中的 `secure` key 已經過加密

+ `config/config` 中的 `API_URI` 未來會用於完善 IOTA Tracker，提供動態選擇 URI 的清單。

+ `config/__init__.py` 中的 `app` 參數是用於 IOTA Tracker 直接寫入資料庫用，和主程式的 `app` 無關。

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform?ref=badge_large)
