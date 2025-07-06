#!/usr/bin/python3
"""
Main file to test the 0-stream_users.py script.
"""
from itertools import islice

# This line imports your stream_users function from the other file.
stream_users = __import__('0-stream_users').stream_users

# This for loop iterates over your generator.
# islice(stream_users(), 6) takes only the first 6 items yielded
# by your generator without trying to fetch everything.
print("Streaming first 6 users:")
for user in islice(stream_users(), 6):
    print(user)