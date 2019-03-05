import requests
main_url = "https://data.broadinstitute.org/bbbc/image_sets.html"
from bs4 import BeautifulSoup

def test_b3_unavailable():
    url = main_url.replace('bbb', 'ccc')
    r = requests.get(url)
    assert r.ok != True


def test_b3_available():
    r = requests.get(main_url)
    assert r.ok


def test_b3_ds006():
    url = "https://data.broadinstitute.org/bbbc/BBBC006/"
    r = requests.get(url)
    assert r.ok
    assert r.content
    assert r.headers


def test_check_ds006_title():
    url = "https://data.broadinstitute.org/bbbc/BBBC006/"
    r = requests.get(url)
    assert r.ok
    soup = BeautifulSoup(r.text, 'html.parser')
    assert soup.title.string
    print(soup.title.string)
