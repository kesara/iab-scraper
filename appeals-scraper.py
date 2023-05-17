import re
import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit
from urllib.parse import urljoin
from weasyprint import HTML

BASE_URL = 'https://www.iab.org'
URL = f'{BASE_URL}/appeals/'


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

    # save markdown
    markdown = md(str(main_content))

    # write to markdown file
    with open(f'{filename}.md', 'w') as file:
        file.write(markdown)
        print(f'saved to {filename}.md')

    # check if images are present
    if len(main_content.find_all('img')) > 0:
        # save PDF file
        html = f'<html><head></head><body>{main_content}</body></html>'
        HTML(string=html, base_url=BASE_URL).write_pdf(f'{filename}.pdf')
        print(f'saved to {filename}.pdf')

def save_pdf(url, filename):
    ''' Download and save PDF file.'''
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
        print(f'saved to {filename}')

response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# find appeal entries
appeals = soup.select('tr:not(:first-of-type)') 

# process appeals
for appeal in appeals:
    tds = appeal.find_all('td')
    # get meeting date
    date = tds[0].text
    match  = re.search(r'\d{4}-\d{2}-\d{2}', date)
    if match:
        date = match.group()
    else:
        stderr.write(f'Can not determine meeting date from {date}')
        exit(1)
    print(f'processing appeal on {date}')

    appeal = tds[1].text

    # check appeal link
    appeal_link = tds[1].find('a')
    appeal_md = None
    if appeal_link:
        appeal_link = urljoin(BASE_URL, appeal_link['href'])

        if appeal_link.endswith('pdf'):
            save_pdf(appeal_link, f'{date}-appeal.pdf')
        else:
            save_content(appeal_link, f'{date}-appeal')

    status = tds[2].text

    # check responses
    responses = tds[2].find_all('a')
    
    # IAB response
    response_link = responses[0]['href']
    if response_link.endswith('pdf'):
        save_pdf(response_link, f'{date}-response.pdf')
    else:
        save_content(response_link, f'{date}-response')

    # replies for response
    if len(responses) == 2:
        reply_link = responses[1]['href']
        if reply_link.endswith('pdf'):
            save_pdf(reply_link, f'{date}-reply.pdf')
        else:
            save_content(reply_link, f'{date}-reply')

    # save yaml
    data = {
        'date': date,
        'appeal': appeal,
        'status': status,
        }
    with open(f'{date}-data.yaml', 'w') as file:
        yaml.dump(data, file)
        print(f'saved to {date}-data.yaml')
