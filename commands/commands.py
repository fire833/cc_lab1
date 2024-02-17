from argparse import ArgumentParser
from templates.v1 import template as v1tmpl
from templates.v1_1 import template as v1_1tmpl
from templates.v1_2 import template as v1_2tmpl
from templates.v2 import template as v2tmpl
from templates.v2_1 import template as v2_1tmpl
from templates.v2_2 import template as v2_2tmpl
import numpy as np
import jinja2
import sys
import subprocess
import os
import random
import csv
import json

templates = {
	"v1": v1tmpl,
	"v1.1": v1_1tmpl,
	"v1.2": v1_2tmpl,
	"v2": v2tmpl,
	"v2.1": v2_1tmpl,
	"v2.2": v2_2tmpl,
}

def new_parser():
	p = ArgumentParser(prog=sys.argv[0], description="Wrapper scripts/utilities for Lab 1 Metaprogramming", add_help=True, allow_abbrev=True)
	sub = p.add_subparsers(title="subcommands")
	
	if os.name == "windows":
		progOut = "./prog.exe"
	else:
		progOut = "./prog"

	gen = sub.add_parser("generate")
	gen.add_argument("--pattern", help="Provide the pattern you want to generate against (should be a string with spaces)", type=str, dest="pattern")
	gen.add_argument("--template", help="Provide the template you want to generate from, current values are (v1)", type=str, default="v1", dest="template")
	gen.add_argument("--outputs", help="Provide the output location of the generated program source.", type=str, default="./prog.c", dest="outputs")
	gen.add_argument("--output", help="Provide the output location of the generated program executable.", type=str, default=progOut, dest="output")
	gen.add_argument("--compiler", help="Provide the path/name of your desired compiler.", type=str, default="gcc", dest="compiler")
	gen.add_argument("--openmp", help="Specify whether to compile the metaprogram with OpenMP enabled.", type=bool, default=False, dest="openmp")
	gen.add_argument("--asm", help="Specify whether to generate an output assembly program for analysis with a tool like OSACA.", type=bool, default=True, dest="asm")
	gen.add_argument("--unroll", help="Specify the amount of outputs to compute per iteration when loop unrolling. Only used with v2 template.", type=int, default=1, dest="unroll")
	gen.set_defaults(func=generate)
	r = sub.add_parser("run")
	r.add_argument("--values", help="Provide a comma-separated list of integers to pass to the generated program.", type=str, dest="values")
	r.add_argument("--input", help="Provide a path to the generated program to execute.", type=str, default=progOut, dest="input")
	r.set_defaults(func=run)
	rrand = sub.add_parser("runrand")
	rrand.add_argument("--input", help="Provide a path to the generated program to execute.", type=str, default=progOut, dest="input")
	rrand.add_argument("--iter", help="Provide the number of iterations you want to execute.", type=int, default=50, dest="iterations")
	rrand.add_argument("--argc", help="Provide the number of arguments that are expected in your generated program.", type=int, dest="argc")
	rrand.add_argument("--arga", help="Provide the number of additional arguments that are expected in your generated program.", type=int, dest="arga")
	rrand.set_defaults(func=run_rand)
	rrprt = sub.add_parser("runreport")
	rtest = sub.add_parser("runtests")

	return p

def runner(args: ArgumentParser):
	# print(args)
	if sys.argv[1] == "generate":
		print("generating new output program")
		return generate(args.pattern, args.template, args.outputs, args.output, args.compiler, args.asm, args.openmp, args.unroll)
	elif sys.argv[1] == "run":
		print("running output program")
		return run(args.input, [int(arg) for arg in args.values.split(",")])
	elif sys.argv[1] == "runrand":
		print("running output program with random inputs")
		return run_rand(args.input, args.iterations, args.argc, args.arga)
	elif sys.argv[1] == "runreport":
		print("running reporting")
		return run_report([("0,1 2,3", 4), ("0 1", 2), ("0,1", 2), ("0,1,2,3 4,5,6,7", 8), ("0 1 2 3 4 5", 6), ("0,1 2,3 4,5 6,7 8,9", 10)], templates.keys(), "./outputs")
	elif sys.argv[1] == "runtests":
		print("running tests")
		return run_tests(templates.keys())

def generate(pattern: str, template: str, outputs: str, output: str, compiler: str, asm: bool, omp: bool, unroll_len: int):
	if templates[template]:
		values = []
		arg_count = 0

		for s in pattern.split(" "):
			values.append([int(arg) for arg in s.split(",")])

		for outer in values:
			for v in outer:
				arg_count += 1

		mult_pairs = len(values)

		unroll_lens = []
		urn_len = unroll_len
		while urn_len > 0:
			unroll_lens.append(urn_len)
			urn_len //=2

		env = jinja2.Environment()
		t = env.from_string(templates[template])
		f = open(file=outputs, mode="w")
		f.write(t.render(mult_pairs=mult_pairs, arg_count=arg_count, sums=values, unroll_len=unroll_len, unroll_lens=unroll_lens))
		f.close()

		args = [compiler, "-O3", "-Wall", "-o", output]
		if omp:
			args.append("-fopenmp")
		if asm:
			args.append("-S")
			args.append(outputs)
			subprocess.run(args)
			args.pop(len(args) - 1)
			args.pop(len(args) - 1)

		args.append(outputs)
		subprocess.run(args)
	else:
		print("please specify a valid template to use")

def run(input: str, args: [int]):
	parsed = ""

	for i in args:
		parsed += f"{i},"

	return json.loads(subprocess.run([input, str(len(args)), parsed.rstrip(",")], capture_output=True).stdout.decode()) 

def run_rand(input: str, iterations: int, arg_count: int, additional_args: int):
	s = arg_count + additional_args
	outputs = []

	for i in range(iterations):
		outputs.append(run(input, [int(random.randint(1,1000)) for i in range(s)]))

	return outputs

def run_report(patterns: [(str, int)], tmplversions: [str], output: str):
	for tmpl in tmplversions:
		for pattern in patterns:
			pat = pattern[0].replace(" ", "_").replace(",", "-")
			out = f"{output}/{tmpl}_{pat}"

			for i in range(2):
				doOpenMP = False
				csvfile = f"{output}/{tmpl}_{pat}.csv"
				if i == 1:
					csvfile = f"{output}/{tmpl}_{pat}_omp.csv"
					doOpenMP = True

				generate(pattern[0], tmpl, out + ".c", out, "gcc", False, doOpenMP, 1000)
				outputs = run_rand(out, 250, pattern[1], 20000)
				write_csv(outputs, csvfile)

def write_csv(outputs, output: str):
	f = open(output, "w")
	f.write("TIMINGS\n")
	for out in outputs:
		if out["compute"]:
			v = out["compute"]
			f.write(f"{v}\n")

	f.close()

def run_tests(tmplversions: [str]):
	tests = [
		("0,1 2,3", [1,2,3,4], [21]),
		("0,1 2,3", [1,2,3,4,5], [21, 45]),
		("0,1 2,3", [1,2,3,4,5,6], [21, 45, 77]),
		("0,1", [1,2,3,4,5,6], [3, 5, 7, 9, 11]),
		("0", [1,2,3,4,5,6,7,8], [1, 2, 3, 4, 5, 6, 7, 8]),
		("0", [1], [1]),
		# ("0", [1,2,3,4,5,6], [1, 2, 3, 4, 5, 6]),
		("0,1,2 3", [1,2,3,4,5], [24, 45]),
		("0,1,2 3", [1,2,3,4,5,1], [24, 45, 12]),
		("0 1 2 3", [0,2,3,4,1,2,3], [0, 24, 24, 24]),
		("0,1,2,3", [0,2,3,4,1,2,3], [9, 10, 10, 10]),
		("0,1,2,3 4 5", [3,4,5,1,2,3,5], [78, 180]),
		("0,2,3 1", [5,4,3,2,1,2,3,4], [40, 21, 12, 7, 16]),
		("1,2,3 0", [5,3,7,5,6,2,2,4], [75, 54, 91, 50, 48]),
		("0,2,1 2,1,0 2,0,1", [10,9,8,7,6,5,4,6,7,21,7,132,65,23], [19683, 13824, 9261, 5832, 3375, 3375]),
		("2,1 0,3", [5,4,6,3,7,2,8], [80, 99, 80, 99]),
		("2,1 0", [5,4,6,3], [50, 36]),
	]

	tOut = f"tests/test"
	for tmpl in tmplversions:
		for (i, test) in enumerate(tests):
			for doOmp in range(2):
				if doOmp == 1:
					generate(test[0], tmpl, f"tests/test_{tmpl}_{i}_omp.c", tOut, "gcc", False, True, 5)
				else:
					generate(test[0], tmpl, f"tests/test_{tmpl}_{i}.c", tOut, "gcc", False, False, 5)
				res = run(tOut, test[1])
				if not res["values"]:
					print(f"test {i} failed version {tmpl} omp: {doOmp}: no values outputs")
					exit(1)
				else:
					outputArr = np.array(res["values"])
					expectedArr = np.array(test[2])
					if (np.array_equal(outputArr, expectedArr)):
						print(f"test {i} passed version {tmpl} omp: {doOmp}")
					else:
						print(f"test {i} failed version {tmpl} omp: {doOmp}, comparison inequality")
						exit(1)
