import csv
import glob
import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit
from weasyprint import HTML

CSV = './statements.csv'
BASE_URL = 'https://www.iab.org/'


def save_content(url, filename):
    '''Save content as markdown. If image is present, save the PDF as well.'''

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # find and delete breadcrumbs
    breadcrumbs = soup.find('div', {'class': 'page_hierarchy'})
    if breadcrumbs:
        breadcrumbs.decompose()

    # find the main content of the page
    main_content = soup.find('div', {'class': 'entry-content'})

    # content fixes
    for header in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        br_tags = header.find_all('br')

        for br_tag in br_tags:
            br_tag.replace_with(' ')

    # save markdown
    markdown = md(str(main_content))

    # write to markdown file
    with open(f'{filename}.md', 'w') as file:
        file.write(markdown)
        print(f'saved to {filename}.md')

    # check if images are present
    if len(main_content.find_all('img')) > 0:
        # save PDF file
        style = '<style>img { max-width: 100%; }</style>'
        html = f'<html><head>{style}</head><body>{main_content}</body></html>'
        HTML(string=html, base_url=BASE_URL).write_pdf(f'{filename}.pdf')
        print(f'saved to {filename}.pdf')

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

        increment = 0
        original_date = date
        while glob.glob(f'{date}.*'):
            increment += 1
            date = f'{original_date}-{increment}'

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
            save_content(url, date)
