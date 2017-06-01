import argparse

from lxml.html import document_fromstring
import requests
import ujson

parser = argparse.ArgumentParser(description='Tom Thumb crawler')
parser.add_argument('filepath', metavar='filepath', nargs=1,
                   help='filepath to the pages JSON file')

START_URL = "https://www.legalstart.fr/"


def get_pages_from_file(filename):
    """
    :type filename: basestring
    :rtype: dict
    """
    with open(filename, 'r') as f:
        return ujson.load(f)


def check_page_and_get_next_url(page, url):
    """

    :type page: dict
    :type url: str

    :raises: TemperedData
    :return: Next page URL xpath test passes, raises TemperedData otherwise
    :rtype: dict
    """
    response = requests.get(url)
    response.raise_for_status()

    doc = document_fromstring(response.content)

    xpath_result = doc.xpath(page["xpath_test_query"])

    if xpath_result == page["xpath_test_result"]:
        return doc.xpath(page['xpath_button_to_click'])[0].get('href')

    raise TemperedData


class TemperedData(ValueError):
    pass


def start():
    pages = get_pages_from_file(parser.parse_args().filepath[0])
    page_number = 0
    page = pages["0"]
    next_url = ''

    while True:
        # Use absolute URLinstead of URI
        if not next_url.startswith('http'):
            next_url = START_URL + next_url

        try:
            next_url = check_page_and_get_next_url(page, next_url)
        except TemperedData as e:
            print("ALERT - Can't move to page {next_page}: page {current_page} link has been "
                  "malevolently tampered with!!".format(
                    next_page=page_number + 1, current_page=page_number))
            break

        page_number += 1
        print("Move to page %s " % page_number)
        page = pages[page['next_page_expected']]


if __name__ == "__main__":
    start()
