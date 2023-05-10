import re
import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit
from urllib.parse import urljoin

BASE_URL = 'https://www.iab.org'
URL = f'{BASE_URL}/appeals/'


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
            # download and save PDF file
            response = requests.get(appeal_link)
            with open(f'{date}-appeal.pdf', 'wb') as file:
                file.write(response.content)
                print(f'saved to {date}-appeal.pdf')
        else:
            markdown = get_markdown(appeal_link)
            with open(f'{date}-appeal.md', 'w') as file:
                file.write(markdown)
                print(f'saved to {date}-appeal.md')

    status = tds[2].text

    # check responses
    responses = tds[2].find_all('a')
    
    # IAB response
    markdown = get_markdown(responses[0]['href'])
    with open(f'{date}-response.md', 'w') as file:
        file.write(markdown)
        print(f'saved to {date}-response.md')

    # replies for response
    if len(responses) == 2:
        markdown = get_markdown(responses[1]['href'])
        with open(f'{date}-reply.md', 'w') as file:
            file.write(markdown)
            print(f'saved to {date}-reploy.md')

    # save yaml
    data = {
        'date': date,
        'appeal': appeal,
        'status': status,
        }
    with open(f'{date}-data.yaml', 'w') as file:
        yaml.dump(data, file)
        print(f'saved to {date}-data.yaml')
