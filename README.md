# Food Frenzy

This is a miniature implementation of a backend service (Python + FastAPI + SqlAlchemy) for a food delivery platform along with the relational database (PostgreSQL)

# API interface

####  List Restaurants API

This is a GET API which has been built to serve the purpose of retrieving a list of restaurants given some conditions. Conditions are supported via query params and the corresponding filters are applied to the resultant list.
######  API Spec
```
GET /api/restaurant
Query-Params: filter=ndish&ndish_gt=13&filter=price&price_lower=10&filter=open_at&open_at=1621197971&limit=1

Response 200 Ok
{"status":"success","restaurants":[{"id":576,"name":"Ember Urban Eatery"}]}
```

**Note**: Response above is just for demo purpose and does not correspond to the request.

##### API Spec details

###### Query-Params or filters supported

###### Filter Open at
| filter        | filter_params           
| ------------- |:-------------:|
| filter=open_at      | open_at=1621197971 |

`open_at` filter helps in filtering restaurants that are open at a certain datetime. To use this filter query_params need to specify the filter type by sending `filter=open_at`. Datetime can be specified via sending query_param `open_at=1621197971` along with the filter type specified as before. Datetime value expected is a **Unix timestamp** in int format. This means do not convert the timestamp into a string. **Note**: If datetime is not explicitly specified, datetime (in UTC) at the time of making the API call is assumed by the API.
Example usage:
```
GET /api/restaurant?filter=open_at&open_at=1621201330
```

###### Filter Price
| filter        | filter_params           
| ------------- |:-------------:|
| filter=price      | price_lower=100 |
| filter=price      | price_upper=200 |
| filter=price      | price_upper=200&price_lower=100 |

`price` filter helps in filtering restaurants that are offering dishes in between a particular price band. To use this filter, send query_params specifying the filter type `filter=price`. Price band can be specified via sending query_params `price_lower=100` and `price_upper=200`. Both `price_lower` and `price_upper` can specify a `float` value. **Note** If `filter=price` is specified by query_params, at least one of the `price_lower` or `price_upper` are required. Of course both can be specified according to needs.
Example usage:
```
GET /api/restaurant?filter=price&price_lower=10&price_upper=40
```

###### Filter Restaurant by dish count served
| filter        | filter_params           
| ------------- |:-------------:|
| filter=ndish      | ndish_gt=10 |
| filter=ndish      | ndish_lt=20 |

`ndish` filter helps in filtering restaurants that are offering no of dishes in a particular range. To use this filter, send query_params specifying the filter type `filter=ndish`. Count range can be specified via sending query_params `ndish_gt=10` and `ndish_lt=20`. Both `ndish_gt` and `ndish_lt` can specify an `Integer` value. **Note** if `filter=ndish` is specified by query_params, at least one of the `ndish_gt` or `ndish_lt` are required to be present in query_params. If both are specified, preference is given to `ndish_gt` and `ndish_lt` becames moot.
Example usage:
```
GET /api/restaurant?filter=ndish&ndish_gt=10
```

###### Limit
`limit` filter helps in limiting restaurants returned to a certain number. To use this filter, send query_params specifying the limit `limit=10`. `limit` can specify an `Integer` value.
Example usage:
```
GET /api/restaurant?limit=10
```

**NOTE: All the above filters can be used in conjunction to each other and combined to create more complex filters. Eg. filters price, ndish and limit can be combined to serve "List top y restaurants that have more or less than x number of dishes within a price range" type queries.
If no filter is specified, open_at is assumed by default by the API by design**

##### Response Spec
```
Response Schema
{
    "status": "success",
    "restaurants": [
        {
            "id": <id>,
            "name": <name>,
        },...
    ]
}
```

#### Search API

This is a GET API which has been built to serve the purpose of searching and retrieving a list of restaurants or dishes where name of the said restaurant or dish matches the incoming search string. Results returned are ranked by relevance to search term.

######  API Spec
```
GET /api/search
Query-Params: s=Tasty

Response 200 Ok
{"status":"success","restaurants":[],"dishes":[{"id":10557,"restaurant_id":1244,"dish_name":"Kanduli Sinigang - A tasty fresh-water fish with miso (bean curd) and fresh mustard leaves.","price":12.02},{"id":12093,"restaurant_id":1422,"dish_name":"Tasty Skoal Whole Rye","price":11.78}]}
```

##### API Spec details
###### Query Param (Search string s)
Search API supports accepting search terms and strings via query params. To search for restaurants or dishes with a string, send an API request to the API with query_params specifying the search string as `s=<search string here>`.

Example usage:
```
GET /api/search?s=Tasty
GET /api/search?s=Steak
GET api/search?s=fish%20steak
```

##### Response Spec
```
Response Schema
{
    "status": "success",
    "restaurants": [
        {
            "id": <id>,
            "name": <name>,
        },...
    ],
    "dishes": [
        {
            "id": <id>,
            "restaurant_id": <restaurant_id>,
            "dish_name": <dish_name>,
            "price": <price>
        },...
    ]
}
```
#### Cart Process API

This is a POST API which has been built to serve the purpose of processing a user purchasing a dish from a restaurant and handling all the data changes. As a result of this API, we get a user transaction record.

######  API Spec
```
POST /cart/process
Body:
Content-Type: application/json
{
    "restaurant_id": <restaurant_id>, // id generated by database after ingesting data.
    "dish_id": <dish_id>, // id generated by database after ingesting data.
    "user_id": <user_id> // Original user id from the data
}

Response 200 Ok
{
    "status": "success",
    "result": {
        "id": 9309,
        "restaurant": 1,
        "menu_item": 1,
        "transaction_amount": 13.88,
        "transaction_date": "2021-05-16T20:19:55.875990"
    }
}
```

##### API Spec details
###### Request Bodu
`restaurant_id` is a integer value which points to the restaurant record.
`dish_id` is a integer value which identifies the dish along with the `restaurant_id`.
`user_id` is the integer id (also found in the raw data), which indentifies the user.

Example usage:
```
curl --location --request POST 'localhost:8000/api/cart/process/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "restaurant_id": 1,
    "dish_id": 1,
    "user_id": 1
}'
```

##### Response Spec
```
Response Schema
{
    "status": "success",
    "result": {
        "id": <user transaction id>,
        "restaurant": <restaurant_id>,
        "menu_item": <dish_id>,
        "transaction_amount": <price of the purchase>,
        "transaction_date": <datetime when transaction happened>
    }
}
```

**NOTE**: You can also see the API interface in Swagger UI by visiting http://localhost:8000/docs on the running server.

# Quick Setup using Docker

This setup is just for the purpose of quickly spinning up the env and play with things. Ideally I wouldn't wanna create db connection string this way.
#### Steps:
* Export the following variables in your terminal.
    * `export DEBUG=True`
    * `export POSTGRES_PASSWORD="<somepassword>"`
    * `export DATABASE_CONN_STR="postgresql://postgres:<samepasswordhere>@db:5432/postgres"`
    * `export INIT_DB=true`
* Run Docker compose `docker-compose up`

Docker will start pulling postgres and building the food frenzy app. Web server may fail to start the very first time due to database connectivity issue (database not ready yet).
Please stop docker images and do `docker-compose up` again to restart.

**NOTE**: `INIT_DB` controls database table creation and also populating the database using the raw datasets available. This runs the ETL scripts and as a result would be slow. This would slow down the start so wait for web server to start.

**NOTE: `INIT_DB=true` should only be used for first time startup. Once data is populated we do not want to run the ETL scripts again. They are not idempotent by design.** 

# Detailed Build Instructions.

You can do this with or without a venv but I am gonna try include usage of a venv in the instructions.

* Make sure you have python 3.8 installed.
* Make sure you have PostgreSQL 12 installed.
* `pip3 install virtualenv`
* Extract the project zip I sent you and open up a terminal to the project folder location.
*  `virtualenv app-frenzy-venv` This will create a virtual env.
*  `source app-frenzy-venv/bin/activate`
*  `pip install -r requirements.txt`

### Create a database inside postgresql to be used in the app.
* Drop to psql shell. `psql`
* `CREATE DATABASE app_frenzy;`
* `CREATE USER app_frenzy WITH PASSWORD <password here>;`
* `ALTER ROLE app_frenzy SET client_encoding TO 'utf8';`
* `ALTER ROLE app_frenzy SET default_transaction_isolation TO 'read committed';`
* `ALTER ROLE app_frenzy SET timezone TO 'UTC';`
* `GRANT ALL PRIVILEGES ON DATABASE app_frenzy TO app_frenzy;`

### Export required env variables
* `export DATABASE_CONN_STR='postgresql://app_frenzy:<userpassword>@localhost:5432/app_frenzy'`
* `export DEBUG=True`

### Create database tables
Run the following command after activating the virtual env to run init-db script.

`python scripts/init-db.py`

### Run the ETL script
Run the following command after activating the virtual env to run populate-db script.

**Note: Do not run the ETL script multiple times since it isn't idempotent**

`python scripts/populate-db.py`

### Run the server (Dev)
Run the following command after activating the virtual env to run development server.

`python main.py`

Make sure you run this from the project directory.

### Run the server (with gunicorn process manager)
Run the following command after activating the virtual env

`bash entrypoint.sh`
