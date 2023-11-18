#!/usr/bin/env python3
"""
Get the domains and locations of the authors from OpenReview.
"""
import argparse
import logging

import pandas
import requests

_LOG = logging.getLogger(__name__)

_URL_API = "https://api2.openreview.net"
_HTTP_TIMEOUT = 5  # seconds


def get_author_domain(author_id, i=0):
    """
    Get the domain of the most recent affiliation of the author.
    """
    if not author_id.startswith("~"):
        dom = author_id.split("@")[-1]
        _LOG.info("Author: %5d :: %s domain: %s", i, author_id, dom)
        return dom

    response = requests.get(f"{_URL_API}/profiles?id={author_id}", timeout=_HTTP_TIMEOUT)
    profiles = response.json().get("profiles", [])
    dom = max(
        ((float(pos.get("end") or "inf"),
          float(pos.get("start") or "-inf"),
          pos.get("institution", {}).get("domain", ""))
         for prof in profiles for pos in prof.get("content", {}).get("history", [])),
        default=(float("inf"), float("-inf"), ""))[2]

    dom = dom.split("@")[-1]
    _LOG.info("Author: %5d :: %s domain: %s", i, author_id, dom)
    return dom


def domains_cleanup_map(domains):
    """
    Replace subdomains with the corresponding parent domains.
    TODO: come up with a more optimal way of doing it.
    """
    domains = sorted(set(domains))
    for i in range(len(domains) - 1):
        for j in range(i + 1, len(domains)):
            if domains[i].endswith(domains[j]):
                tail = domains[j].split(".")
                if domains[i].split(".")[-len(tail):] == tail:
                    _LOG.info("Replace domains: %s -> %s", domains[i], domains[j])
                    yield (domains[i], domains[j])


def _main():

    parser = argparse.ArgumentParser(
        description="Scrape OpenReview for locations of the authors.")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    df = pandas.read_csv(args.input)
    authors_set = frozenset(df.author)
    _LOG.info("Num papers: %d from unique authors: %d", len(df), len(authors_set))
    domains = {
        author: get_author_domain(author, i)
        for (i, author) in enumerate(authors_set)
    }
    cleanup_map = dict(domains_cleanup_map(domains.values()))
    domains = {
        author: cleanup_map.get(domains[author], domains[author])
        for author in domains
    }
    df["domain"] = df.author.map(domains)
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s'
    )
    _main()
