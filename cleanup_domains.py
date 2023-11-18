#!/usr/bin/env python3
"""
Remove the subdomains from the domain names, where possible.
"""
import argparse
import logging

import pandas

_LOG = logging.getLogger(__name__)


def domains_cleanup_map(domains):
    """
    Replace subdomains with the corresponding parent domains.
    TODO: come up with a more optimal way of doing it.
    """
    res = {}
    domains = sorted(set(domains), key=lambda s: s[::-1], reverse=True)
    for i in range(len(domains) - 1):
        for j in range(i + 1, len(domains)):
            if domains[i].endswith(domains[j]):
                tail = domains[j].split(".")
                if len(tail) > 1 \
                   and domains[i].split(".")[-len(tail):] == tail \
                   and tail[0] not in {"edu", "org", "ac"}:
                    _LOG.info("Replace: %s -> %s", domains[i], domains[j])
                    res[domains[i]] = domains[j]
    return res


def _main():
    parser = argparse.ArgumentParser(
        description="Clean up the domain names in the data.")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    df = pandas.read_csv(args.input)
    domains = dict(zip(df.domain, df.domain))
    domains.update(domains_cleanup_map(df.domain.fillna("")))
    df["domain"] = df.domain.map(domains)
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s'
    )
    _main()
