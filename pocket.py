#!/usr/bin/env python3
import os

import requests
from jmespath import search as jmes
from rich.console import Console


def retrieve(key, token):
    url = f"https://getpocket.com/v3/get?consumer_key={key}&access_token={token}&detailType=complete"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Couldn't retrieve Pocket list")


def select(body):
    return [
        {
            "title": entry["resolved_title"],
            "url": f"https://getpocket.com/read/{entry['item_id']}",
            "length": (
                entry.get("time_to_read")
                or sum([int(t) for t in jmes("videos.*.length", entry) or []]) // 60
            ),
            "tags": jmes("tags.*.tag", entry),
        }
        for entry in jmes("list.*", body)
    ]


def sort(items):
    return sorted(items, key=lambda i: i["length"] or float("inf"))


def prettify(items):
    text = ""
    for index, item in enumerate(items):
        text += (
            f"[i cyan]{index+1}.[/i cyan]"
            f" [b green link={item['url']}]{(item['title'] or item['url']).title()}[/b green link]"
            f"\n{(item.get('length') or '??'):>3}🕛"
            f" {' '.join([f'[blue]🏷️{i}[/blue]' for i in item.get('tags') or []])}"
            "\n\n"
        )

    return text


if __name__ == "__main__":
    key = os.environ.get("POCKET_CONSUMER_KEY")
    token = os.environ.get("POCKET_ACCESS_TOKEN")
    console = Console(force_terminal=True)
    console.print(prettify(sort(select(retrieve(key, token)))))
