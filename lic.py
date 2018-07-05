import os
from base64 import b64decode as decode

h = os.environ['QHOME']
l = decode(os.environ['QLIC_KC'])
with open(os.path.join(h, 'kc.lic'), 'wb') as f:
    f.write(l)
