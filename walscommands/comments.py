"""
Parse comments from HTML files as served from the WP admin view.
"""
import collections

from bs4 import BeautifulSoup as bs
from clldutils.jsonlib import dump

from cldfbench_wals import Dataset


def run(args):
    ds = Dataset()
    comments = {}
    for p in ds.raw_dir.glob('blog_comments/comments*.html'):
        for c in iter_comments(p):
            comments[c['id']] = c
    comments = sorted(comments.values(), key=lambda c: int(c['id'].split('comment-')[-1]))
    dump(comments, ds.etc_dir / 'comments.json', indent=4)
    args.log.info('{} comments'.format(len(comments)))


def parse_comment(tr):
    post_link = tr.find('div', class_='response-links').find('a')
    return collections.OrderedDict([
        ('id', tr['id']),
        ('author', {
            'name': tr.find('div', class_='author').string,
            'url': tr.find('div', class_='author-url').string,
        }),
        ('status', tr.find('div', class_='comment_status').string),
        ('text', tr.find('textarea', class_='comment').string),
        ('date', tr.find('div', id='submitted-on').find('a').string.split(' at')[0]),
        ('post', {
            'id': post_link['href'].split('post=')[-1],
            'title': post_link.string,
        }),
    ])


def iter_comments(p):
    table = bs(p.read_text(encoding='utf8'), 'html.parser').find('tbody', id="the-comment-list")
    for tr in table.find_all('tr'):
        yield parse_comment(tr)
