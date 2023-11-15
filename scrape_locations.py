#!/usr/bin/env python3
"""
Get the domains and locations of the authors from OpenReview.
"""
import argparse
import logging

import pandas
import whois

_LOG = logging.getLogger(__name__)


def get_location(domain):
    """
    Get the country and state of the domain.
    """
    if domain is None:
        return (None, None, None)
    w = whois.whois(domain)
    country = w.country or w.registrant_country
    state = w.state or w.registrant_state
    city = w.city or w.registrant_city
    _LOG.info("Domain: %s Location: %s, %s, %s", domain, country, state, city)
    return (country, state, city)


def _main():
    parser = argparse.ArgumentParser(
        description="Use whois to get the locations of the authors' domains.")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    df = pandas.read_csv(args.input)
    domains = list(
        df.groupby("domain").count().sort_values("author", ascending=False).index
    )
    locations = {domain: get_location(domain) for domain in domains}
    df["country"] = df.domain.map(lambda d: locations[d][0])
    df["state"] = df.domain.map(lambda d: locations[d][1])
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s'
    )
    _main()
