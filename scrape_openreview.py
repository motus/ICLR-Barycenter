#!/usr/bin/env python3
"""
Scrape OpenReview for IDs the authors.
Default conference is ICLR 2023.
"""
import argparse
import logging
import re

import pandas
import requests
from bs4 import BeautifulSoup

_LOG = logging.getLogger(__name__)

# Scrape HTML instead of using REST API so we don't have to login.
_URL_ROOT = "https://openreview.net"

_RE_LAST_PAGE = re.compile(r"/submissions\?page=(\d+)&.*")
_HTTP_TIMEOUT = 5  # seconds


def get_venues(conference, year):
    """
    Get the list of all conference's venues.
    """
    response = requests.get(
        f"{_URL_ROOT}/venue?id={conference}", timeout=_HTTP_TIMEOUT)
    soup = BeautifulSoup(response.text, "html.parser")
    href_regex = re.compile(rf"/submissions\?venue={conference}/{year}/.*")
    return [a['href'].split("=")[1] for a in soup.find_all("a", href=href_regex)]


def get_authors(venue, max_pages=None):
    """
    Fetch all pages of the conference venue and extract the IDs of the authors.
    For each paper, yield a triplet of (author_id, author_index, num_authors).
    """
    page = 1
    while max_pages is None or page <= max_pages:

        _LOG.info("Get authors for venue: %s page: %d of %s", venue, page, max_pages)
        response = requests.get(
            f"{_URL_ROOT}/submissions?venue={venue}&page={page}", timeout=_HTTP_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")

        for (i, paper) in enumerate(soup.find_all("div", {"class": "note-authors"})):
            authors = paper.find_all("a")
            num_authors = len(authors)
            _LOG.debug("Paper %d has %d authors", i, num_authors)
            for (author_idx, author_id) in enumerate((a['title'] for a in authors), 1):
                yield (author_id, author_idx, num_authors)

        page += 1
        if max_pages is None:
            last_page = soup.find_all("a", href=_RE_LAST_PAGE)[-1:]
            max_pages = (
                int(_RE_LAST_PAGE.match(last_page[0]['href']).group(1))
                if last_page else 0
            )


def _main():

    parser = argparse.ArgumentParser(
        description="Scrape OpenReview for IDs the authors.")
    parser.add_argument("--conference", default="ICLR.cc")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    venues = get_venues(args.conference, args.year)
    _LOG.info("Venues:\n  * %s", "\n  * ".join(venues))

    df = pandas.DataFrame(
        data=(
            (venue, author, author_pos, num_authors)
            for venue in venues
            for (author, author_pos, num_authors) in get_authors(venue)
        ),
        columns=["venue", "author", "author_pos", "num_authors"]
    )

    fname_output = args.output or f"{args.conference.split('.')[0]}_{args.year}.csv"
    df.to_csv(fname_output, index=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s'
    )
    _main()
