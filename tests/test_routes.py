from datetime import datetime, date, timedelta

ARTICLE_TITLE = "Albert_Einstein"
TEST_DATE = (date.today() - timedelta(days=60)).strftime("%Y-%m-%d")

def test_invalid_date_error(client):
    response = client.get(f'/articles/most-viewed/{TEST_DATE.replace("20", "2X")}')
    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert response.json["data"]["message"] == f"""Invalid date provided. Please use YYYY-MM-DD (eg. {
                    date.today().strftime('%Y-%m-%d')
                }) format."""

def test_most_viewed_monthly(client):
    response = client.get(f"/articles/most-viewed/{TEST_DATE}")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["period"] == "monthly"
    assert len(response.json["data"]) > 0

def test_most_viewed_weekly(client):
    response = client.get(f"/articles/most-viewed/{TEST_DATE}?period=weekly")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["period"] == "weekly"
    assert len(response.json["data"]) > 0

def test_article_count_monthly(client):
    response = client.get(f"/articles/{ARTICLE_TITLE}/{TEST_DATE}")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["period"] == "monthly"
    assert response.json["data"]["views"] > 0
    assert response.json["data"]["article"] == ARTICLE_TITLE

def test_article_count_weekly(client):
    response = client.get(f"/articles/{ARTICLE_TITLE}/{TEST_DATE}?period=weekly")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["period"] == "weekly"
    assert response.json["data"]["views"] > 0
    assert response.json["data"]["article"] == ARTICLE_TITLE

def test_article_most_day(client):
    response = response = client.get(f"/articles/{ARTICLE_TITLE}/{TEST_DATE}/most")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["data"]["views"] > 0
    assert datetime.strptime(response.json["data"]["date_most_views"], "%Y-%m-%d") is not Exception
    assert response.json["data"]["article"] == ARTICLE_TITLE
