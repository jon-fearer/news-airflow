import re
import requests


def parse_cnn(title, url):
    response = requests.get(url)
    find_paragraph = '(?:<p class="zn-body__paragraph speakable">|' + \
                     '<div class="zn-body__paragraph speakable">|' + \
                     '<div class="zn-body__paragraph">).+?(?:</p>|</div>)'
    paragraphs = re.findall(find_paragraph, response.text, re.DOTALL)
    article = ' '.join(paragraphs)
    if not article:
        return title
    div = '<[^>]+>'
    match = re.search(div, article, re.DOTALL)
    while match:
        article = article.replace(match.group(0), '')
        match = re.search(div, article, re.DOTALL)
    with open('../data/{}.txt'.format(title[:20]), 'w') as f:
        f.write(article)
