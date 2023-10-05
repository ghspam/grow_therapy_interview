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
uwsgi --http 127.0.0.1:8080 --master -p 4 -w app:app
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

## Contributing

Please don't.

## Road Map

Here are some ideas for improving this project:

* languages/region support - Wikipedia has many other regions and languages it serves and these are often referred to as "projects" in Wikipedia world. This project only covers the English language "project". Adding a parameter to the URL could improve the available statistical data.
* stats for other types of data - This project only covers PageView statistics. The Wikipedia API is vast and could collect stats from many other types of query-able information, such as users/contributors and categories.
* caching results - The code runs a fresh API query on every call. I'm sure Wikipedia is caching that data, but this code could also cache results in something fun like a sqlite database.
* limit returned results - Some of the endpoints will return 1000 items. A good way to help speed up response times would be to slice that 1000 item long list with a URL query param.
* configuration - The project is mostly hardcoded with it's configurable variables. Some ideas for different configuration options are: threading workers, rate limiting, other sources/API endpoints, http port/host
* tests can always be improved (mock data) - perhaps in conjunction with the caching support
* shrink the container image - Currently my basic python:3.11 container image is whopping 1.03GB. Much too big for a small application
