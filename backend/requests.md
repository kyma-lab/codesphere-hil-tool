
## contribute

- uses test.txt as simulated annotated data (test.txt is an IOB2 format file with annotated data)
- install jq with `sudo apt install jq`
- returns code 200 on success

`curl http://127.0.0.1:8070/api/contribute -d "{\"userid\": \"TESTUSER\", \"texts\":[$(jq -Rs . < material/test.txt)]}" -H 'Content-Type: application/json' -vvv  -H "cookie: hil-user-id=TESTUSER" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxMzc2ODEyMywianRpIjoiNmJjNjA1ODEtODRkMS00NGUyLWFiZTAtNjI2NjE2MTI3Y2E4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3R1c2VyIiwibmJmIjoxNzEzNzY4MTIzLCJjc3JmIjoiM2Q5ZjBjMDEtYzI2YS00MWE1LWEzNjYtOWNiYmE3MmY1Njg2IiwiZXhwIjoxNzEzODU0NTIzfQ.edv14kcqiVAE_ZSrVOYgpS47evPezEWQOnCU-gFQiDw"`

```
> POST /api/contribute HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.88.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 3334
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/2.2.3 Python/3.9.5
< Date: Mon, 21 Aug 2023 09:34:24 GMT
< Content-Type: application/json
< Content-Length: 3
< Connection: close
```

## get predictions 

- uses input.txt as simulated non-annotated input data (input.txt is an IOB2 format file with only O annotations)
- returns IOB2 formatted annotated data (same as in request, but with the predicted annoations)
- (in this demo the data does not match, the returned data is of different length and from a different dataset)

`curl http://127.0.0.1:8080/api/getpredictions -d '{"userid": "TESTUSER", "texts": ["$(cat material/input.txt)"]} -H 'Content-Type: application/json' -vvv`

with time-tracking

`curl -o /dev/null -s -w 'Establish Connection: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n'   http://127.0.0.1:8080/api/getpredictions   -d '{"userid": "TESTUSER", "texts": ["$(cat material/input.txt)"]}'   -H 'Content-Type: application/json' -vvv`

```
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> POST /api/getpredictions HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.88.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 7130
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/2.2.3 Python/3.9.5
< Date: Mon, 21 Aug 2023 09:44:39 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 3335
< Connection: close
< 
The O
primacy O
of O
either O
species B-Quality
...
... (redacted for brevity)
...
allowed O
to O
freely O
choose O
among O
the O
available O
plant B-Organism
species I-Organism
. O
* Closing connection 0
```

## extract

- login on frontend, make a request, and take the auth token from that

```
curl -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwOTU1MDk0OSwianRpIjoiOWIwOTQwZDMtMDJmZi00OGJiLThjMTUtYjU3MmUxODUwNTZiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3R1c2VyIiwibmJmIjoxNzA5NTUwOTQ5LCJjc3JmIjoiNjhiNGM0NTQtZjQ0Yy00NWQ5LWJhODktZmZjMzc1MDhkZThkIiwiZXhwIjoxNzA5NjM3MzQ5fQ.HT9w9hjIqsF0PgCUxITvZPifPKR0G_tJ2Ogp1cvE32s" -F "file=@/home/robin/Documents/test.pdf" http://localhost:8080/api/extract
```