# Grab function and description from code.kx.com which still uses mediawiki
# Requires Python 3.6+

from pickle import dump
from urllib.parse import urljoin

import py
import requests
from bs4 import BeautifulSoup as bs

KWDS = ['abs', 'acos', 'aj', 'aj0', 'all', 'and', 'any', 'asc', 'asin', 'asof',
        'atan', 'attr', 'avg', 'avgs', 'bin', 'binr', 'ceiling', 'cols', 'cor', 'cos',
        'count', 'cov', 'cross', 'csv', 'cut', 'delete', 'deltas', 'desc', 'dev',
        'differ', 'distinct', 'div', 'do', 'dsave', 'each', 'ej', 'ema', 'enlist',
        'eval', 'except', 'exec', 'exit', 'exp', 'fby', 'fills', 'first', 'fkeys',
        'flip', 'floor', 'get', 'getenv', 'group', 'gtime', 'hclose', 'hcount',
        'hdel', 'hopen', 'hsym', 'iasc', 'idesc', 'if', 'ij', 'in', 'insert',
        'inter', 'inv', 'key', 'keys', 'last', 'like', 'lj', 'ljf', 'load',
        'log', 'lower', 'lsq', 'ltime', 'ltrim', 'mavg', 'max', 'maxs', 'mcount',
        'md5', 'mdev', 'med', 'meta', 'min', 'mins', 'mmax', 'mmin', 'mmu', 'mod',
        'msum', 'neg', 'next', 'not', 'null', 'or', 'over', 'parse', 'peach', 'pj',
        'prd', 'prds', 'prev', 'prior', 'rand', 'rank', 'ratios', 'raze', 'read0',
        'read1', 'reciprocal', 'reval', 'reverse', 'rload', 'rotate', 'rsave', 'rtrim',
        'save', 'scan', 'scov', 'sdev', 'select', 'set', 'setenv', 'show', 'signum',
        'sin', 'sqrt', 'ss', 'ssr', 'string', 'sublist', 'sum', 'sums', 'sv', 'svar',
        'system', 'tables', 'tan', 'til', 'trim', 'type', 'uj', 'ungroup', 'union',
        'update', 'upper', 'upsert', 'value', 'var', 'view', 'views', 'vs', 'wavg',
        'where', 'while', 'within', 'wj', 'wj1', 'wsum', 'ww', 'xasc', 'xbar', 'xcol',
        'xcols', 'xdesc', 'xexp', 'xgroup', 'xkey', 'xlog', 'xprev', 'xrank']

HEADERS = {
    # Let's brake their statistics :)
    'User-Agent': 'Mozilla/2.0 (compatible; MSIE 3.0; Windows 3.1)'
}

CARD = 'http://code.kx.com/q/ref/card/'

out = {}
r = requests.get(CARD, headers=HEADERS)
if r.status_code == requests.codes.ok:
    soup = bs(r.text, 'html.parser')
    for div in soup.find_all('div', {'class': 'md-content'}):
        for link in div.find_all('a'):
            key = link.text.strip().split()[0]
            if 'class' not in link.attrs:
                if key in KWDS:
                    href = urljoin(CARD, link.attrs['href'])
                    title = link.attrs['title'].strip() if 'title' in link.attrs else key
                    # strip unicode characters
                    title = title.encode('ascii', 'ignore').decode().strip()
                    out[key] = (key, title, href)
    print("Missing:", ', '.join(k for k in KWDS if k not in out))
    filename = py.path.local('code.kx.dump')
    with filename.open('wb') as f:
        dump(out, f)

    print(f"Saved into {filename}.")

else:
    print(f"ERROR {r.status_code} downloading page from {CARD}.")
