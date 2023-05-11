import csv
import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit

CSV = './statements.csv'


def get_markdown(url):
    '''Get markdwon from the the URL'''

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # find and delete breadcrumbs
    breadcrumbs = soup.find('div', {'class': 'page_hierarchy'})
    if breadcrumbs:
        breadcrumbs.decompose()

    # find the main content of the page
    main_content = soup.find('div', {'class': 'entry-content'})

    # return markdown
    return md(str(main_content))


with open(CSV, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    # ignore header
    next(reader)

    # go through statments
    for row in reader:
        date = row[0]
        match  = re.search(r'\d{4}-\d{2}-\d{2}', date)
        if match:
            date = match.group()
        else:
            stderr.write(f'Can not determine meeting date from {row[0]}')
            exit(1)
        print(f'processing statement on {date}')

        url = row[2]
        pdf_url = row[3]

        if pdf_url and pdf_url.endswith('pdf'):
            # download and save PDF file
            response = requests.get(pdf_url)
            with open(f'{date}.pdf', 'wb') as file:
                file.write(response.content)
                print(f'saved to {date}.pdf')
        else:
            # get markdown for the statment
            markdown = get_markdown(url)

            # write to file
            with open(f'{date}.md', 'w') as file:
                file.write(markdown)
                print(f'saved to {date}.md')
