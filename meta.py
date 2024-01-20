#!/usr/bin/env python

import jinja2
import sys
import os
from templates.v1 import template as v1tmpl

def main():
	values = []
	arg_count = 0

	for s in sys.argv[1:]:
		values.append([int(arg) for arg in s.split(",")])

	for outer in values:
		for v in outer:
			arg_count += 1

	mult_pairs = len(values)

	env = jinja2.Environment()
	t = env.from_string(v1tmpl)
	f = open(file="./prog.c", mode="w")
	f.write(t.render(mult_pairs=mult_pairs, arg_count=arg_count, sums=values))
	f.close()

if __name__ == '__main__':
	main()
