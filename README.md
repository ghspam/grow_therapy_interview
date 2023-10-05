# grow therapy interview project

An API server designed to return various statistics from the English language Wikipedia API.

## Requirements

* Python v3
* Pip
* Docker (optional)
* A good attitude

## Install

Clone the repository and then activate a virtual environment:

```sh
$ cd grow_therapy_interview
$ python -m venv .venv
$ . .venv/bin/activate
```

Great job, you're well on your way to Wikipedia statistical nivrana! Now use `pip` to install the dependencies. Like so:

```sh
pip install -r requirements.txt
```

Now we're cookin'. Now you need to decide if you want a development environment or not. I have a friend who prefers production, we call him Production Patrick. If you're more of a Production Patrick instead of a Development Daniel (my other friend), continue to the __Production environment__ section.

### Development environment

It's easiest to just run Flask in debug mode:

```sh
flask run --debug
```

### Production environment

This project uses `uwsgi` a WSGI server. If you're not interested in running this locally or if you let out a big sigh at the start of the install section you may be interested in using a container instead please see the __Docker (optional)__ section.

To start the wsgi production environment with for load-balancing processes:

```sh
uwsgi --http 127.0.0.1:8000 --master -p 4 -w app:app
```

## Docker (optional)

Okay so you just want to deploy the dang thing. All you need is container to show off to your friends how powerful you are with your new found knowledge of Wikipedia statistics. You don't care about python or it's best practices, just those meaty wiki stats.

First build the container with:

```sh
docker build --tag grow_therapy-docker .
```

Then run the container (do not use `-d` if you do not want to daeomonize):

```sh
docker run -d -p 8000:8000 grow_therapy-docker
```

## Documentation

The code is fairly well documented, however some may prefer to prevent sore eyes by reading __pretty__ documentation. To generate the docs run:

```sh
pdoc3 --html app.py
```

## Tests

This project uses `pytest` to run 6 (count'em) e2e route tests. To run the tests:

```sh
pytest 
```

## API Endpoints

### /articles/most-viewed/{date}

__Most Viewed Stats for a Wikipedia article__
    
Accepts a `date` (YYYY-MM-DD) and optional query param `period` of `monthly` (default) or `weekly` and returns list of articles and total article views for the specified period.
    
#### Examples:

##### Monthly

```sh
curl -XGET "http://127.0.0.1:8000/articles/most-viewed/2023-09-15" // returns top 1000 viewed articles for the month of September (09).
```

##### Weekly

```sh
curl -XGET "http://127.0.0.1:8000/articles/most-viewed/2023-09-15?period=weekly" // returns top 1000 viewed articles for the week of September 15 (Sept 11 - Sept 17)
```

#### Args:
rdate (str): requested relative date (to `period`, default is `monthly`) retrieve article stats (default: today's date)

#### Query Params:
period (enum[monthly*|weekly]): monthly or weekly period to query

#### Returns:
JSON: List of most viewed articles and respective view count for specified period

### /articles/{article_title}/{date}

__View Stats for a Single Article on a specific date__

Accepts a date and returns stats for a given optional period of monthly (default) or weekly and returns total view count.

#### Examples:

##### Monthly

```sh
curl -XGET "http://127.0.0.1:8000/articles/Albert_Einstein/2023-09-15" // returns top 1000 viewed articles for the week of September 15 (Sept 11 - Sept 17)
```

##### Weekly

```sh
curl -XGET "http://127.0.0.1:8000/articles/Albert_Einstein/2023-09-15?period=weekly" // returns top 1000 viewed articles for the week of September 15 (Sept 11 - Sept 17)
```

#### Args:
atitle (str): string of article to check for
rdate (str): requested relative date to retrieve article stats (default: today's date)

#### Query Params:
period (enum[monthly*|weekly]): monthly or weekly period to query

#### Returns:
JSON: Name of article with total views for specified date

### /articles/{article_title}/{date}/most

View day of month where article has most views

Accepts a date and article title and returns day of month in which article has most views.

#### Examples:

```sh
curl -XGET "http://127.0.0.1:8000/articles/Albert_Einstein/2023-09-15"
```

#### Args:
atitle (str): string of article title to check for
rdate (str): requested relative date to retrieve article view count (default: `date.today()`)

#### Returns:
JSON: object containing article title and date which had most views and view count

## Contributing

Please don't, this project is unmaintained.

## Road Map

Here are some ideas for improving this project:

* __languages/region support__ - Wikipedia has many other regions and languages it serves and these are often referred to as "projects" in Wikipedia world. This project only covers the English language "project". Adding a parameter to the URL could improve the available statistical data.
* __stats for other types of data__ - This project only covers PageView statistics. The Wikipedia API is vast and could collect stats from many other types of query-able information, such as users/contributors and categories.
* __caching results__ - The code runs a fresh API query on every call. I'm sure Wikipedia is caching that data, but this code could also cache results in something fun like a sqlite database.
* __limit returned results__ - Some of the endpoints will return 1000 items. A good way to help speed up response times would be to slice that 1000 item long list with a URL query param.
* __configuration__ - The project is mostly hardcoded with it's configurable variables. Some ideas for different configuration options are: threading workers, rate limiting, other sources/API endpoints, http port/host
* __tests can always be improved (mock data)__ - perhaps in conjunction with the caching support
* __shrink the container image__ - Currently my basic python:3.11 container image is whopping 1.03GB. Much too big for a small application
