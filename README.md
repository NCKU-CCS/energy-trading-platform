# energy-trading-platform

[![Build Status](https://travis-ci.org/NCKU-CCS/energy-trading-platform.svg?branch=cswang%2Fet_platform)](https://travis-ci.org/NCKU-CCS/energy-trading-platform)

## [GET] address

+ 提供 AMI Data Uploader 來詢問上傳的 IOTA Address

+ Address 規則：
    + 每個 field 對應到一個 Address
    + 每小時更新一次 Address

+ token 作為 Uploader 的認證

### Database

+ postgres docker

    `docker pull postgres`

+ run with db data

    `docker run --name mypostgres -e POSTGRES_PASSWORD=password -v "$PWD/db":/var/lib/postgresql/data -p 5432:5432 -d postgres`

### 連接方式

+ 參數
    + token : 認證用
    + field : 每個 field 會有不同對應的 Adderss
