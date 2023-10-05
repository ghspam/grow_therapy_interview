"""Smol API to return article stats from Wikipedia"""
import calendar
import concurrent.futures
import json
import requests
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify

# pylint: disable=line-too-long
MOST_VIEWED_BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/"
ARTICLE_PAGEVIEW_BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/"
# pylint: enable=line-too-long

app = Flask(__name__)

@app.route("/articles/most-viewed/<rdate>")
def most_viewed_stats(rdate = date.today()):
    """Most Viewed Stats for a Wikipedia article
    
    Accepts a `date` (YYYY-MM-DD) and optional query param `period` of `monthly` (default)
    or `weekly` and returns list of articles and total article views for the specified period.
    
    For example:

    date = 2023-09-15 and period = monthly
    
    The above input will return top 1000 viewed articles for the month of September (09).
    
    Args:
        rdate (str): requested relative date to retrieve article stats (default: today's date)
    
    Returns:
        JSON: List of most viewed articles and respective view count for specified period
    """
    # define `period` query param and retrieve default value
    period = get_period(request)

    # set date range
    # check date
    parsed_date = None
    try:
        parsed_date = check_date(rdate)
    except Exception as e:
        print(e)
        return json_error()

    # get date_range for api call
    date_range = get_date_range(parsed_date, period)

    # loop through dates and use threads to concurrently retrieve data
    # set article data into k/v dict
    article_stats = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_requests = {executor.submit(query_wiki, f'{MOST_VIEWED_BASE_URL}{wiki_date.strftime("%Y/%m/%d")}'): wiki_date for wiki_date in date_range}
        # process future responses into JSON list response
        for future in concurrent.futures.as_completed(future_requests):
            wiki_response = future.result()
            if wiki_response.status_code != 200:
                continue

            wiki_data = json.loads(wiki_response.content)
            wiki_items = wiki_data["items"][0]["articles"]
            for item in wiki_items:
                if item["article"] not in article_stats:
                    article_stats[item["article"]] = 0
                article_stats[item["article"]] += int(item["views"])

    # create list of article_stats values
    unsorted_data = [{"article": atitle, "views": aviews} for atitle, aviews in article_stats.items()]
    result_data = sorted(unsorted_data, key=lambda i: i["views"], reverse=True)
    return jsonify({"status": "success", "data": result_data, "period": period})


@app.route("/articles/<atitle>/<rdate>")
def aritcle_stats(atitle, rdate = date.today()):
    """View Stats for a Single Article on a specific date
    
    Accepts a date and returns stats for a given optional period of monthly (default) or weekly and 
    returns total view count.
    
    Args:
        atitle (str): string of article to check for
        rdate (str): requested relative date to retrieve article stats (default: today's date)
    
    Returns:
        JSON: Name of article with total views for specified date
    """
    period = get_period(request)
    try:
        parsed_date = check_date(rdate)
    except Exception as e:
        print(e)
        return json_error()
    date_range = get_date_range(parsed_date, period)

    full_url = f'{ARTICLE_PAGEVIEW_BASE_URL}{atitle}/daily/{date_range[0].strftime("%Y%m%d")}00/{date_range[-1].strftime("%Y%m%d")}00'
    total_views = 0
    wiki_response = query_wiki(full_url)
    raw_data = json.loads(wiki_response.content)
    for i in raw_data["items"]:
        total_views += i["views"]

    return jsonify({"status": "success", "period": period, "data": {"article": raw_data["items"][0]["article"], "views": total_views}})

@app.route("/articles/<atitle>/<rdate>/most")
def article_top(atitle, rdate = date.today()):
    """View day of month where article has most views
    
    Accepts a date and article title and returns day of month in which article has most views.
    
    Args:
        atitle (str): string of article title to check for
        rdate (str): requested relative date to retrieve article view count (default: `date.today()`)
    
    Returns:
        JSON: object containing article title and date which had most views and view count
    """
    try:
        parsed_date = check_date(rdate)
    except Exception as e:
        print(e)
        return json_error()
    date_range = get_date_range(parsed_date, "monthly")
    full_url = f'{ARTICLE_PAGEVIEW_BASE_URL}{atitle}/daily/{date_range[0].strftime("%Y%m%d")}00/{date_range[-1].strftime("%Y%m%d")}00'
    wiki_response = query_wiki(full_url)
    raw_data = json.loads(wiki_response.content)
    most_views = {}
    for i in raw_data["items"]:
        if "views" not in most_views or most_views["views"] > i["views"]:
            most_views = i
    formatted_date = datetime.strptime(most_views["timestamp"], "%Y%m%d00").strftime("%Y-%m-%d")
    return jsonify({"status": "success", "data": {"article": raw_data["items"][0]["article"], "date_most_views": formatted_date, "views": most_views["views"]}})


"""Helper Funcs

    Functions to DRY it up
"""
def get_period(r):
    """Return valid period query arg"""
    period_list = ["monthly", "weekly"]
    period = r.args.get("period", default = "monthly", type = str)
    if period not in period_list:
        period = "monthly"
    return period

def check_date(rdate):
    """Parses raw date and returns date object or throws exception"""
    return datetime.strptime(rdate, "%Y-%m-%d")

def get_date_range(parsed_date, period):
    """Parse and retrieve date_range for specified period and parsed_date"""
    date_range = None
    if period == "weekly":
        # for weekly, grab first day of week (current day - current day week day)
        # and last day of week (first day + 6 days)
        week_start = parsed_date - timedelta(days=parsed_date.weekday())
        date_range = generate_date_range(week_start, 7)
    else:
        # for monthly retrieve first day of month (always 01)
        # and last day of month (current month + 1 month - 1 day)
        start_date = parsed_date - timedelta(days=parsed_date.day - 1)
        pd_year = parsed_date.year
        pd_month = parsed_date.month
        total_days = calendar.monthrange(pd_year, pd_month)[1]
        date_range = generate_date_range(start_date, total_days)
    return date_range

def generate_date_range(start_date, total_days):
    """Generate a list of dates from specified range
    
    Accepts a start_date and total_days that will generate a list of date objects
    
    Args:
        start_date (date): date to begin generating date objects
        total_days (int): total number of days to generate dates for list
    
    Returns:
        list: generated dates from specified input
    """
    return [start_date + timedelta(days=x) for x in range(total_days)]

def query_wiki(query_url):
    """Queries wikipedia url for provided date_str
    
    Accepts a url to query.
    Then returns raw response object.
    
    Args:
        url (string): url to make GET request
    
    Returns:
        requests.response: raw wikipedia api request response
    """
    print(query_url)
    return requests.get(
        query_url,
        headers={"user-agent": "interview/me+growtherapy@alexkavon.com"},
        timeout=10000
    )

def json_error():
    """Format and return JSON error"""
    return jsonify({
        "status": "error",
        "data": {
            "message":
            f"""Invalid date provided. Please use YYYY-MM-DD (eg. {
                    date.today().strftime('%Y-%m-%d')
                }) format."""
        }
    }), 400

if __name__ == '__main__':
    app.run(debug=True)
