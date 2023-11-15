#!/usr/bin/env python3
"""
Get the domains and locations of the authors from OpenReview.
"""
import argparse
import logging

import pandas
import whois
import requests

_LOG = logging.getLogger(__name__)

_URL_API = "https://api2.openreview.net"
_HTTP_TIMEOUT = 5  # seconds


def get_author_domain(author_id):
    """
    Get the domain of the most recent affiliation of the author.
    """
    response = requests.get(f"{_URL_API}/profiles?id={author_id}", timeout=_HTTP_TIMEOUT)
    profiles = response.json()["profiles"]
    dom = max((pos["end"] or float("inf"), pos["start"], pos["institution"]["domain"])
              for prof in profiles for pos in prof["content"]["history"])[2]
    _LOG.info("Author: %s domain: %s", author_id, dom)
    return dom


def get_location(domain):
    """
    Get the country and state of the domain.
    """
    w = whois.whois(domain)
    country = w.country or w.registrant_country
    state = w.state or w.registrant_state
    _LOG.info("Domain: %s Location: %s / %s", domain, country, state)
    return (country, state)


def _main():
    parser = argparse.ArgumentParser(
        description="Scrape OpenReview for locations of the authors.")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    df = pandas.read_csv(args.input)
    domains = {
        author: get_author_domain(author)
        for author in set(df.author_id)
    }
    locations = {
        domain: get_location(domain)
        for domain in set(domains.values())
    }
    df["domain"] = df.author_id.map(domains)
    df["country"] = df.domain.map(lambda d: locations[d][0])
    df["state"] = df.domain.map(lambda d: locations[d][1])
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _main()
