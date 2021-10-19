import os
print(os.environ['PYTHONPATH'])
from utils import inline_stats
import numpy as np
import numpy.random as r

def test_inline_stats():
    arr = r.randint(2000, 5000, 1000)
    inline_stats(arr)


