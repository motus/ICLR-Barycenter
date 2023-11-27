#!/usr/bin/env python3
"""
Extract the airports' IATA codes from ChatGPT responses.
"""
import re
import csv
import argparse

import nltk
import pandas

_RE_IATA = re.compile(r"^[A-Z]{3}$")


def _main():
    parser = argparse.ArgumentParser(
        description="Extract the airports' IATA codes from ChatGPT responses.")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    tokenizer = nltk.tokenize.wordpunct_tokenize

    df = pandas.read_csv(args.input)
    df['airport'] = None
    for (i, row) in df.iterrows():
        airports = set(t for t in tokenizer(row.response) if re.match(_RE_IATA, t))
        airports.difference_update(
            tokenizer(row.domain.upper()) +
            ["USA", "ETH", "IIT", "BJR", "LRC", "MBA", "ROT"]
        )
        df.loc[i, 'airport'] = "|".join(list(airports)[-1:])

    df.to_csv(args.output, index=False, quoting=csv.QUOTE_ALL)


if __name__ == "__main__":
    _main()
