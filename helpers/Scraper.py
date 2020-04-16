import requests
from bs4 import BeautifulSoup as Soup
import urllib.parse


class Scraper:
    pages_to_visit = []
    visited = []
    MAIN_SLUG = 'main'
    CONFIG = {}

    def __init__(self, CONFIG):
        self.CONFIG = CONFIG

        self.add_page_to_visit(
            self.CONFIG[self.MAIN_SLUG]['start_url'], self.MAIN_SLUG)

        step = self.get_step_from_slug()
        step_name = self.get_step_name_from_slug()

        self.handle_pages()

    def get_result_by_type(self, step, item):
        """
        GET REQUIRED DATA
        Get the data from the provided css query selector, based on the step type
        """

        result = ''

        if step['type'] == 'link':
            # If the link is relative, make it absolute
            result = urllib.parse.urljoin(
                self.CONFIG['main']['start_url'], item['href'])
        if step['type'] == 'text':
            result = item.string

        if 'replace' in step:
            # Replace the searched term with the provided one
            result = result.replace(step['replace'][0], step['replace'][1])

        return result

    def get_html(self, current_url):
        """
        GET HTML
        Get the html from the url provided
        """

        req = requests.get(current_url)
        return Soup(req.content, 'html.parser')

    def get_results(self, html, step):
        """
        GET RESULTS
        Get the results based on the css query selector
        """

        # Get the results starting from the provided selector
        results = [self.get_result_by_type(step, target)
                   for target in html.select(step['target'])]

        # If multiple is not allowed, returns only one
        if ('multiple' not in step or step['multiple'] == False) and len(results) > 0:
            results = [results[0]]

        return results

    def add_page_to_visit(self, url, new_step):
        """
        ADD PAGE TO VISIT
        Add a new page to be visited
        """

        full_step = self.get_next_step_slug()
        last_step = self.get_step_name_from_slug()

        if not last_step:
            step = self.MAIN_SLUG
        elif new_step == last_step or new_step == full_step:
            step = self.get_next_step_slug()
        else:
            step = self.get_next_step_slug()+"."+new_step

        if url not in self.visited:
            # Add to be visited
            self.pages_to_visit.append(
                {
                    'url': url,
                    'step': step,
                }
            )

            # Add to visited
            self.visited.append(url)

    def scrape_page_and_children(self, html):
        self.scrape_page(html)
        self.scrape_children(html)

    def save_to_file(self, text):
        file = open("results.txt", "a")
        file.write(text+'\n\n')
        file.close()

    def scrape_page(self, html, step=None, step_name=None):
        """
        SCRAPE PAGE
        Actaully scrapes the page
        """

        # Get info about the current step
        current_step = step or self.get_step_from_slug()
        current_step_name = step_name or self.get_next_step_slug()

        # Handle the page scraping (only when step is not "main")
        results = self.get_results(
            html, current_step) if current_step_name != self.MAIN_SLUG else []

        if(len(results) > 0):
            for result in results:
                if current_step['type'] == 'text':
                    print('   +++ text found +++', result)
                    self.save_to_file(result)

                    # TODO save as csv (make it changeable in the config)
                else:
                    print('   +++ link found +++', result)

                if current_step['type'] == 'link':
                    # Append the result to links to visit if they are not in the list
                    self.add_page_to_visit(result, current_step_name)

    def scrape_children(self, html):
        current_step = self.get_step_from_slug()
        current_step_name = self.get_next_step_slug()

        if current_step_name == 'main' or (('simultaneous' in current_step and current_step['simultaneous'] == True) and ('steps' in current_step and len(current_step['steps']) > 0)):
            for step_name, step in current_step['steps'].items():
                self.scrape_page(html, step=step, step_name=step_name)

    def handle_pages(self):
        while len(self.pages_to_visit) > 0:
            # Get the url to scan
            current_url = self.get_next_url()

            # Get the html
            html = self.get_html(current_url)

            print('++++++++++', current_url, '++++++++++')

            # Actually scrapes the page
            self.scrape_page_and_children(html)

            # Remove the first step from the array of the ones to be visited
            self.go_to_next_url()

    def get_next_url(self):
        return self.pages_to_visit[0]['url'] if len(self.pages_to_visit) else None

    def get_next_step_slug(self):
        return self.pages_to_visit[0]['step'] if len(self.pages_to_visit) else None

    def get_step_from_slug(self):
        slug = self.get_next_step_slug()
        final_slug = self.CONFIG

        for step in '.steps.'.join(slug.split('.')).split('.'):
            final_slug = final_slug[step]

        return final_slug

    def get_step_name_from_slug(self):
        slug = self.get_next_step_slug()

        return slug.split('.')[-1] if slug else None

    def go_to_next_url(self):
        self.pages_to_visit.pop(0)
