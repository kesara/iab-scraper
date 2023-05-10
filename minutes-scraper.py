import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit

URL= 'https://www.iab.org/documents/minutes/'


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

# find minutes entries
main_content = soup.find('div', {'class': 'entry-content'})
ul_list = main_content.find_all('ul', {'class': 'children'})

# find all the child list items
for ul in ul_list:
    li_list = ul.find_all('li')

    for li in li_list:
        url = li.find('a')['href']
        if url:
            # get meeting date
            match  = re.search(r'\d{4}-\d{2}-\d{2}', url)
            if match:
                date = match.group()
            else:
                stderr.write(f'Can not determine meeting date for {url}')
                exit(1)

            print(f'getting {url}')
            markdown = get_markdown(url)

            # write to file
            with open(f'{date}.md', 'w') as file:
                file.write(markdown)
                print(f'saved to {date}.md')
