#!/usr/bin/env python

import requests
import sys
from optparse import OptionParser

import csv
import re

FILE_NAME = 'pull-requests.csv'

repo_url = "https://api.github.com/repos/MarlinFirmware/Marlin/pulls"
token = 'XXX'


def get_pull_requests(begin, end, clean=False):
    if clean:
        write_pull_req_csv_heading()

    for number in range(begin, end, -1):
        get_commits_for_pr(number)


def get_commits_for_pr(pull_request):
    url = "{}/{}/commits".format(repo_url, pull_request)
    response = get(url)
    if response.status_code != 200:
        print("PR#{} : {} --- {}".format(pull_request, response.status_code, response.text))
    else:
        content_json = response.json()
        append_pull_req_json_to_csv(pull_request, content_json)


def build_link_navigation(links_header):
    split_links = links_header.split(",")
    links = {}
    for link_blob in split_links:
        m = re.match(r".*page=(\d+)>; rel=\"(\w*)\"", link_blob)
        page, rel = m.groups()
        links[rel] = page

    return links


def get(url):
    return requests.get(url, headers={'Authorization': 'token ' + token})


def write_pull_req_csv_heading():
    with open(FILE_NAME, 'w') as csv_file:
        csv.writer(csv_file).writerow([
            "pr",
            "sha",
            "author",
            "committer",
            "mergemessage",
            "url",
            "#parents"
        ])


def append_pull_req_json_to_csv(pull_request, json):
    with open(FILE_NAME, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        for commit in json:
            csv_writer.writerow([
                pull_request,
                commit["sha"],
                commit["author"].get("login"),
                commit["committer"].get("login"),
                "Merge" in commit["commit"]["message"],
                commit["url"],
                len(commit["parents"])
            ])

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", action="store_true", dest="clean", default=False)
    (options, args) = parser.parse_args(sys.argv)
    begin = int(args[1])
    end = int(args[2])
    if end < begin:
        get_pull_requests(begin, end, options)
