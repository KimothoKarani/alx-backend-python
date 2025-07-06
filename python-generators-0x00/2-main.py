#!/usr/bin/python3
"""
Main file to test the 1-batch_processing.py script.
"""
import sys

# This imports your 1-batch_processing.py file as a module
processing = __import__('1-batch_processing')

# This block calls your batch_processing function and handles a specific error
try:
    # This is the main call to your function with a batch size of 50
    processing.batch_processing(50)
except BrokenPipeError:
    # This prevents a "BrokenPipeError" from showing up when you use
    # commands like `head`.
    # It happens when the command receiving the output (e.g., `head`)
    # closes the connection before your script is done printing.
    sys.stderr.close()