from pyq import q, K
from matplotlib import pyplot as plt

def read_image(path):
    path = str(path).lstrip(':')
    x = plt.imread(path)
    return K(x)
r = q('{x enlist y}', read_image)
q.set('.im.read', r)

def save_image(path, image):
    path = str(path).lstrip(':')
    plt.imsave(path, image)
q.set('.im.save', save_image)
q).q.imsave:{.im.save(x;y)}
