#!/usr/bin/python3
"""
Main file to test the 2-lazy_paginate.py script.
"""
import sys

# Correctly import the 'lazy_paginate' function
lazy_paginate = __import__('2-lazy_paginate').lazy_paginate

try:
    # Get the generator that will yield pages of 100 users
    for page in lazy_paginate(100):
        # Loop through the users in the currently yielded page
        for user in page:
            print(user)

except BrokenPipeError:
    sys.stderr.close()