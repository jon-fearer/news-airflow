import re
import requests


def parse_cnn(title, url):
    response = requests.get(url)
    find_article = 'id="body-text".+<p class="zn-body__paragraph zn-body__footer">'
    result = re.search(find_article, response.text, re.DOTALL)
    try:
        article = result.group(0)
    except AttributeError:
        return title
    start = '^[^>]+>'
    strip = re.search(start, article, re.DOTALL)
    article = article.replace(strip.group(0), '')
    script = '<script>[^<]+</script>'
    match = re.search(script, article, re.DOTALL)
    while match:
        article = article.replace(match.group(0), '')
        match = re.search(script, article, re.DOTALL)
    div = '<[^>]+>'
    match = re.search(div, article, re.DOTALL)
    while match:
        article = article.replace(match.group(0), '')
        match = re.search(div, article, re.DOTALL)
    article = article.replace(' (CNN)', '')
    with open('{}.txt'.format(title[:20]), 'w') as f:
        f.write(article)
