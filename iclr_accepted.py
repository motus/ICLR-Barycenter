#!/usr/bin/env python3
"""
Scrape OpenReview for IDs the authors.
Default conference is ICLR 2023.
"""
import argparse
import logging

import pandas
import requests
from bs4 import BeautifulSoup

_LOG = logging.getLogger(__name__)

_URL_ROOT = "https://iclr.cc"
_HTTP_TIMEOUT = 5  # seconds


def get_accepted_papers(year):
    """
    Return a list of OpenReview IDs of the papers accepted at ICLR.
    """
    ids = []
    response = requests.get(f"{_URL_ROOT}/virtual/{year}/papers.html", timeout=_HTTP_TIMEOUT)
    soup = BeautifulSoup(response.text, "html.parser")
    for a in soup.find("noscript", {"class": "noscript"}).ul.find_all("a"):
        _LOG.info("Get OpenReview ID for: %s", a['href'])
        response = requests.get(f"{_URL_ROOT}{a['href']}", timeout=_HTTP_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")
        ref = soup.find("a", title="OpenReview")
        if ref:
            ids.append(ref["href"].split("=")[-1])
    return ids


def _main():

    parser = argparse.ArgumentParser(
        description="Scrape ICLR site for OpenReview IDs of accepted papers.")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("input", help="CSV file with submitted papers")
    parser.add_argument(
        "output", default=None,
        help="Output CSV file with the `accepted` column. Same as `input` if not specified.")
    args = parser.parse_args()

    df = pandas.read_csv(args.input)
    if "accepted" not in df.columns:
        df["accepted"] = False

    ids = set(get_accepted_papers(args.year))
    df["accepted"] |= df["paper_id"].isin(ids)

    df.to_csv(args.output or args.input, index=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s'
    )
    _main()
