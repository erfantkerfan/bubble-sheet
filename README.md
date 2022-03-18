## Project setup with Docker:

1. run `cp .env.example .env`
2. configure `APP_PORT` as the web interface port the default is `8050`
3. configure `MASTER_TOKEN` as the master token for administration
4. run `docker-compose up --build -d`
5. in case it's needed to send any inside docker use `docker-compose exec web python main.py --help`

## api documentation

<details>
  <summary> health check </summary>

    GET `/api/health/check`

</details>

### api v1 documentation

<details>
  <summary> scan bubble-sheet sample response </summary>

    POST `/api/v1/scan/test`

</details>


<details>
  <summary> scan bubble-sheet form MinIO source </summary>

    POST `/api/v1/scan/minio`

```json
{
  "token": "hgRHGxrX6yd4Zz5gtSVxDkARcrkjAF_vf7PkkF8jDRA",
  "path": "pics/test.jpg",
  "path_choices": "output_pics/test.jpg"
}
```

</details>


<details>
  <summary> scan bubble-sheet form a url </summary>

    POST `/api/v1/scan/url`

```json
{
  "url": "https://nodes.alaatv.com/test/test.jpg"
}
```

</details>


<details>
  <summary> scan bubble-sheet form a multipart-request </summary>

    POST `/api/v1/scan/direct`

```json
{
  "image": "[FILE.jpg]"
}
```

</details>


<details>
  <summary> detect qrcode sample response </summary>

    POST `/api/v1/detect/test`

</details>


<details>
  <summary> detect qrcode form MinIO source </summary>

    POST `/api/v1/detect/minio`

```json
{
  "token": "hgRHGxrX6yd4Zz5gtSVxDkARcrkjAF_vf7PkkF8jDRA",
  "path": "pics/test.jpg"
}
```

</details>


<details>
  <summary> detect qrcode form a url </summary>

    POST `/api/v1/detect/url`

```json
{
  "url": "https://nodes.alaatv.com/test/test.jpg"
}
```

</details>


<details>
  <summary> detect qrcode form a multipart-request </summary>

    POST `/api/v1/detect/direct`

```json
{
  "image": "[FILE.jpg]"
}
```

</details>


<details>
  <summary> sheet generator using MinIO for storage </summary>

    POST `/api/v1/generate/minio`

```json
{
  "token": "hgRHGxrX6yd4Zz5gtSVxDkARcrkjAF_vf7PkkF8jDRA",
  "path": "output/alaa.zip",
  "data": [
    {
      "name": "عرفان قلی زاده",
      "ostan": "تهران",
      "shahr": "تهران",
      "date": "1400/09/05",
      "duration": "60 دقیقه",
      "start": "07:30",
      "exam_description": "آزمون شماره ۱۲ - پایه دوازدهم ریاضی",
      "qrcode": "71bdcea2cb12aa4141711919,123456789"
    },
    {
      "name": "سهراب ابوذرخانی فرد",
      "ostan": "تهران",
      "shahr": "تهران",
      "date": "1400/09/05",
      "duration": "60 دقیقه",
      "start": "07:30",
      "exam_description": "آزمون شماره 135 - پایه دهم ریاضی تجربی",
      "qrcode": "31bdcea2cb14ea4181711920,987654321"
    },
    {
      "name": "سید دانیال معین آل داوودی سادات پور",
      "ostan": "سیستان و بلوچستان اطراف چهار راه",
      "shahr": "اسلام آباد غرب اصل آباد",
      "date": "1400/09/05",
      "duration": "60 دقیقه",
      "start": "07:30",
      "exam_description": "آزمون شماره 135 - پایه دهم ریاضی تجربی",
      "qrcode": "61bdcea2cb14ea4181711919,111111113"
    }
  ]
}
```

</details>

##### administration

<details>
  <summary> generate a user token </summary>

    POST `/api/v1/token/minio`

```json
{
  "master_token": "PtXQe66HDpI4AVCFu5HSZBW7QEuCDwwuysDhs2hfpvo",
  "endpoint": "nodes.alaatv.com",
  "bucket": "test",
  "access_key": "xxxxxxxxxxxxxxxxx",
  "secret_key": "yyyyyyyyyyyyyyyyyy"
}
```

</details>


<details>
  <summary> remove a user token </summary>

    DELETE `/api/v1/token/minio`

```json
{
  "master_token": "PtXQe66HDpI4AVCFu5HSZBW7QEuCDwwuysDhs2hfpvo",
  "token": "rmT4WoMWYwrdjJF2hDs6bGEU9Uh-Ng3xK9rkLCVxd90"
}
```

</details>


<details>
  <summary> remove all tokens </summary>

    DELETE `/api/v1/token/minio`

```json
{
  "master_token": "PtXQe66HDpI4AVCFu5HSZBW7QEuCDwwuysDhs2hfpvo",
  "token": "all"
}
```

</details>