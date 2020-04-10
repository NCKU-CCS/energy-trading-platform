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
- docker 18.09.7


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

## Notice

+ set Time Zone at `.env` file

+ `.travis.yml` 中的 `secure` key 已經過加密

+ `config/config` 中的 `API_URI` 未來會用於完善 IOTA Tracker，提供動態選擇 URI 的清單。

+ `config/__init__.py` 中的 `app` 參數是用於 IOTA Tracker 直接寫入資料庫用，和主程式的 `app` 無關。

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform?ref=badge_large)