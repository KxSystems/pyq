# Grab function and description from code.kx.com which still uses mediawiki
# Requires Python 3.6+

from time import sleep
from pickle import dump

import py
import requests


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
URL_PATTERN = "http://code.kx.com/wiki/Reference/{}?action=raw"
HEADERS = {
    # Let's brake their statistics :)
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 4.0; Windows NT)'
}

OUT = {}

for kwd in KWDS:
    url = URL_PATTERN.format(kwd)
    r = requests.get(url, headers=HEADERS)
    if r.status_code == requests.codes.ok:
        line = r.text.splitlines()[0]
        try:
            _, func, desc = line.replace('}', '').split('|')
        except ValueError as e:
            print(f"{kwd}: Error {e} - {line}")
            OUT[kwd] = line
        else:
            OUT[kwd] = (func, desc)
            print(f"{kwd}: {func}|{desc}")
    else:
        print(f"{kwd}: Error {r.status_code} downloading from {url}.")
        OUT[kwd] = r.status_code

    sleep(0.5)  # Let's not DDoS them

filename = py.path.local(__file__).new(ext='dump')
with filename.open('wb') as f:
    dump(OUT, f)

print(f"Saved into {filename}.")
