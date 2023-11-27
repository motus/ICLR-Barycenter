#!/usr/bin/env python3
"""
Get the airport codes of the authors of the accepted papers.
"""
import argparse
import csv
import json
import logging

import pandas
from openai import OpenAI, APITimeoutError

_LOG = logging.getLogger(__name__)


_OAI_REQUEST = """
    Good.
    What international airport is the nearest to the {domain} largest campus?
    Respond with 3-letter IATA code.
"""


def get_location(client, domain):
    """
    Get the location of the domain.
    """
    _LOG.info("Domain: %s", domain)
    if domain is None:
        return None
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": _OAI_REQUEST.format(domain=domain)
            }],
            n=1,
            # max_tokens=1,
            temperature=1.5,
            frequency_penalty=-2.0,
            model="gpt-3.5-turbo",
            timeout=5,
        )
        response = chat_completion.choices[0].message.content
        _LOG.info("Response for : %s :: %s", domain, response)
        return response
    except APITimeoutError:
        _LOG.warning("Timeout for %s", domain)
        return None


def _main():
    parser = argparse.ArgumentParser(
        description="Use ChatGPT to get the airports closest to the authors' domains.")
    parser.add_argument("--config", help="JSON config with OpenAI API key")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    with open(args.config, "rt", encoding="utf-8") as f:
        config = json.load(f)

    df = pandas.read_csv(args.input)
    if "response" in df.columns:
        responses = list(df[df.response.notna()].to_records(index=False))
        domains = [dom for dom in df.domain[df.response.isna()]]
    else:
        responses = []
        domains = sorted(dom for dom in set(df.domain[df.accepted])
                         if dom and isinstance(dom, str) and ' ' not in dom)

    client = OpenAI(api_key=config["key"])
    responses += [(dom, get_location(client, dom)) for dom in domains]

    df_out = pandas.DataFrame(data=map(list, responses), columns=["domain", "response"])
    df_out.sort_values("domain").to_csv(args.output, index=False, quoting=csv.QUOTE_ALL)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s'
    )
    _main()
