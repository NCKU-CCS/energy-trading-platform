# energy-trading-platform

[![Build Status](https://travis-ci.org/NCKU-CCS/energy-trading-platform.svg?branch=cswang%2Fet_platform)](https://travis-ci.org/NCKU-CCS/energy-trading-platform)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform?ref=badge_shield)

主要功能為綠能交易平台的 API，詳細資訊：[API Document](https://et01.docs.apiary.io/#)

## [GET] address

+ 提供 AMI Data Uploader 詢問上傳的 IOTA Address

+ Authorization: Bearer Token

+ Address 規則：
    + 每個上傳 AMI 對應到一個 Address
    + 每天更新一次 Address

### Database

+ Running database at background

    `docker-compose up -d`

### IOTA Tracker

+ Get Datas from IOTA and decrypt, based on address from database and tags from configs.

    `pipenv run python pt/iota_tracker.py`

### Notice

+ `.travis.yml` 中的 `secure` key 已經過加密

+ `config/config` 中的 `API_URI` 未來會用於完善 IOTA Tracker，提供動態選擇 URI 的清單。

+ `config/__init__.py` 中的 `app` 參數是用於 IOTA Tracker 直接寫入資料庫用，和主程式的 `app` 無關。

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FNCKU-CCS%2Fenergy-trading-platform?ref=badge_large)