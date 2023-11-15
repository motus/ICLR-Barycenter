#!/usr/bin/env python3
"""
Scrape OpenReview for emails of the authors.
Default conference is ICLR 2023.
"""
import argparse
import logging
import re

import pandas
import requests
from bs4 import BeautifulSoup

_LOG = logging.getLogger(__name__)

# Scrape HTML for papers so we don't have to login.
_URL_ROOT = "https://openreview.net"
_URL_API = "https://api2.openreview.net"

_RE_LAST_PAGE = re.compile(r"/submissions\?page=\d+&.*")
_HTTP_TIMEOUT = 5  # seconds


def get_venues(conference, year):
    """
    Get the list of all conference's venues.
    """
    response = requests.get(
        f"{_URL_ROOT}/venue?id={conference}", timeout=_HTTP_TIMEOUT)
    soup = BeautifulSoup(response.text, "html.parser")
    href_regex = re.compile(rf"/submissions\?venue={conference}/{year}/.*")
    return [a['href'] for a in soup.find_all("a", href=href_regex)]


def get_authors(venue, max_pages=float("inf")):
    """
    Fetch all pages of the conference venue and extract the IDs of the authors.
    For each paper, yield a triplet of (author_id, author_index, num_authors).
    """
    page = 1
    while page <= max_pages:
        _LOG.info("Get authors for venue: %s page: %d of %s", venue, page, max_pages)
        response = requests.get(f"{_URL_ROOT}{venue}&page={page}", timeout=_HTTP_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")
        for paper in soup.find_all("div", {"class": "note-authors"}):
            num_authors = len(paper)
            _LOG.info("Paper %s has %d authors", paper, num_authors)
            for (i, author) in enumerate((a['title'] for a in paper.find_all("a")), 1):
                yield (author, i, num_authors)
        if max_pages is None:
            max_pages = int(soup.find_all("a", href=_RE_LAST_PAGE)[-1].text)
        page += 1


def get_author_domain(author_id):
    """
    Get the domain of the most recent affiliation of the author.
    """
    response = requests.get(f"{_URL_API}/profiles?id={author_id}", timeout=_HTTP_TIMEOUT)
    profiles = response.json()["profiles"]
    return max((pos["end"] or float("inf"), pos["start"], pos["institution"]["domain"])
               for prof in profiles for pos in prof["content"]["history"])[2]


def _main():
    parser = argparse.ArgumentParser(
        description="Scrape OpenReview for locations of the authors.")
    parser.add_argument("conference", default="ICLR.cc")
    parser.add_argument("year", type=int, default=2023)
    parser.add_argument("output", default=None, default=2023)
    args = parser.parse_args()
    venues = get_venues(args.conference, args.year)
    _LOG.info("Venues:\n%s", "\n  * ".join(venues))
    df = pandas.DataFrame(
        data=(
            (args.conference, args.year, venue, author, author_pos, num_authors)
            for venue in venues
            for (author, author_pos, num_authors) in get_authors(venue)
        ),
        columns=["conference", "year", "venue", "author", "author_pos", "num_authors"]
    )
    fname_output = args.output or f"{args.conference}_{args.year}.csv"
    df.to_csv(fname_output, index=False)
