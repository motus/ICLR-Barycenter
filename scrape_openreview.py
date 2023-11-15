#!/usr/bin/env python3
"""
Scrape OpenReview for emails of the authors.
Default conference is ICLR 2023.
"""
import re
# import argparse

import whois
import requests
from bs4 import BeautifulSoup

# conference = "ICLR.cc"
# year = 2023

_URL_ROOT = "https://openreview.net"
_URL_API = "https://api2.openreview.net"

_RE_LAST_PAGE = re.compile(r"/submissions\?page=\d+&.*")
_HTTP_TIMEOUT = 5  # seconds


def get_venues(conference, year):
    """
    Get the list of URLs of all conference's venues.
    """
    response = requests.get(
        f"{_URL_ROOT}/venue?id={conference}", timeout=_HTTP_TIMEOUT)
    soup = BeautifulSoup(response.text, "html.parser")
    href_regex = re.compile(rf"/submissions\?venue={conference}/{year}/.*")
    return [f"{_URL_ROOT}{a['href']}"
            for a in soup.find_all("a", href=href_regex)]


def get_authors(url_venue, max_pages=float("inf")):
    """
    Fetch all pages of the conference venue and extract the IDs of the authors.
    For each paper, yield a triplet of (author_id, author_index, num_authors).
    """
    page = 1
    while page <= max_pages:
        response = requests.get(f"{url_venue}&page={page}", timeout=_HTTP_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")
        for paper in soup.find_all("div", {"class": "note-authors"}):
            num_authors = len(paper)
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


def get_location(domain):
    """
    Get the country and state of the domain.
    """
    w = whois.whois(domain)
    country = w.country or w.registrant_country
    state = w.state or w.registrant_state
    return (country, state)
