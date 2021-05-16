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