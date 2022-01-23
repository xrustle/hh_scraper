# Vacancies parser

Small application for parsing Data Scientist vacancies and saving it to MongoDB.

It consists of two containers: Python application and MongoDB.

## Building and running from source
```console
git clone https://github.com/xrustle/hh_scraper.git

cd hh_scraper
docker-compose up -d
```

## Check parsing results
All vacancies will be stored in the `db.vacancies` collection in `mongo` container.
You can see the list using console:
```console
mongo -u root -p password

use db
db.vacancies.find().pretty()
```
or use Mongo GUI Compass application. Port `27888`. User `root`. Password `password`.
