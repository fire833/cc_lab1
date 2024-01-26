#!/usr/bin/env python

import jinja2
import sys
import os
import argparse
from commands.commands import new_parser

def main():
	p = new_parser()
	opts = p.parse_args()

if __name__ == '__main__':
	main()
