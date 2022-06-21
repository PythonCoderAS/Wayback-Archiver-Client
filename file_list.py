import sys
from argparse import ArgumentParser
from signal import SIGINT, signal
from time import sleep

from requests import Session
from tqdm import tqdm

from shared import add_url, get_session_id

session = Session()


def do(filepath: str):
    with open(filepath, "r") as f:
        lines = f.read().splitlines(False)
    for line in tqdm(lines):
        r = session.get(f"https://web.archive.org/save/" + line, allow_redirects=False)
        retry_count = 1
        while not r.ok and retry_count <= 5:
            sleep(60)
            r = session.get(f"https://web.archive.org/save/" + line, allow_redirects=False)
            retry_count += 1
        if r.ok:
            add_url(session_id, line)


def main(args=None):
    parser = ArgumentParser(description="Archive all the URLS inside a file.")
    parser.add_argument("file", help="The path to the file to archive.")
    parsed = parser.parse_args(args)
    return do(parsed.file)


signal(SIGINT, lambda *_: sys.exit(0))

if __name__ == '__main__':
    session_id: int = get_session_id()
    main()
