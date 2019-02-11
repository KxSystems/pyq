\l p.q
p)import sys, os, pytest
p)sys.argv = ['']
p)from pyq import q
p)os.environ['QBIN'] = str(q('first .z.X'))
p)args = ['--pyargs', 'pyq']
p)args.extend(['-k', 'not test_pyq_executable'])
p)args.extend(str(x) for x in q('2_.z.X'))
exit .p.qeval"pytest.main(args)"
