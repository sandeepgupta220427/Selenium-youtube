import json

a = json.dumps({"name": "Pramod", "age": 30, "city": "New York"})
print(a)

import math

print(math.sqrt(16))

import random

print(random.randint(1, 10))


# Module import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils_extra.utils import printLog,sayHello
from utils_extra.utils import * # Import all the functions

printLog()
sayHello("Pramod")
