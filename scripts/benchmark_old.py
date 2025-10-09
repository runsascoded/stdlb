#!/usr/bin/env python
"""Benchmark old version import time."""
import sys
import subprocess
import time as time_module

def benchmark_old_version(runs=50):
    """Benchmark import time of old version (20 modules)."""
    # Simulate old version - just the original 20 or so modules
    code = """
import base64
from base64 import *
import configparser
from configparser import *
import contextlib
from contextlib import *
import dataclasses
from dataclasses import *
from datetime import *
from datetime import datetime as dt
import datetime
import functools
from functools import *
from glob import *
import glob
import hashlib
from hashlib import *
import io
from io import *
import itertools
from itertools import *
import json
import math
from math import *
import os
from os import *
from os.path import *
import pathlib
from pathlib import *
import re
from re import *
from shlex import *
import shlex
import shutil
from shutil import *
import subprocess
from subprocess import *
import sys
from sys import *
import tempfile
from tempfile import *
from time import *
import time
import traceback
from traceback import *
import typing
from typing import *
import urllib
from urllib import *
import uuid
from uuid import *
import warnings
"""

    times = []
    for _ in range(runs):
        start = time_module.perf_counter()
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
        )
        end = time_module.perf_counter()

        if result.returncode != 0:
            print(f"Import failed: {result.stderr.decode()}")
            return 1

        times.append((end - start) * 1000)

    avg_time_ms = sum(times) / len(times)
    print(f"Old version (~20 modules): {avg_time_ms:.2f}ms average")
    return avg_time_ms

if __name__ == "__main__":
    benchmark_old_version()
