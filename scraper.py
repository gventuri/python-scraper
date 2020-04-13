import requests
from config import CONFIG
from bs4 import BeautifulSoup as Soup
import urllib.parse


def get_required_data(step, item):
    """
    GET REQUIRED DATA
    Get the data from the provided css query selector, based on the step type
    """

    if step['type'] == 'link':
        # If the link is relative, make it absolute
        return urllib.parse.urljoin(CONFIG['start_url'], item['href'])
    if step['type'] == 'text':
        return item.string


current_url = CONFIG['start_url']
req = requests.get(current_url)
for step in CONFIG['steps']:
    html = Soup(req.content, 'html.parser')

    # Maps all the results based on the step type
    results = [get_required_data(step, target)
               for target in html.select(step['target'])]

    # It is not multiple, returns only one
    if not step['multiple'] or step['multiple'] == False:
        results = [results[0]]

print(results)
