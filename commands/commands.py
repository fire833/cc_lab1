from argparse import ArgumentParser
from templates.v1 import template as v1tmpl
from templates.v2 import template as v2tmpl
import jinja2
import sys
import subprocess
import os
import random
import csv
import json

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

	return p

def runner(args: ArgumentParser):
	# print(args)
	if sys.argv[1] == "generate":
		print("generating new output program")
		return generate(args.pattern, args.template, args.outputs, args.output, args.compiler, args.asm, args.openmp)
	elif sys.argv[1] == "run":
		print("running output program")
		return run(args.input, [int(arg) for arg in args.values.split(",")])
	elif sys.argv[1] == "runrand":
		print("running output program with random inputs")
		return run_rand(args.input, args.iterations, args.argc, args.arga)
	elif sys.argv[1] == "runreport":
		print("running reporting")
		return run_report([50], [5,10,50,100,1000,10000], [], ["v1"], "./outputs")

templates = {
	"v1": v1tmpl,
	"v2": v2tmpl
}

def generate(pattern: str, template: str, outputs: str, output: str, compiler: str, asm: bool, omp: bool):
	if templates[template]:
		values = []
		arg_count = 0

		for s in pattern.split(" "):
			values.append([int(arg) for arg in s.split(",")])

		for outer in values:
			for v in outer:
				arg_count += 1

		mult_pairs = len(values)

		env = jinja2.Environment()
		t = env.from_string(templates[template])
		f = open(file=outputs, mode="w")
		f.write(t.render(mult_pairs=mult_pairs, arg_count=arg_count, sums=values))
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

def run_report(iter_sizes: [int], arga_sizes: [int], patterns: [(str, int)], tmplversions: [str], output: str):
	for tmpl in tmplversions:
		for pattern in patterns:
			pat = pattern[0].replace(" ", "_").replace(",", "-")
			out = f"{output}/{tmpl}_{pat}"
			generate(pattern[0], tmpl, out + ".c", out)
			for iter in iter_sizes:
				for arga in arga_sizes:
					col = f"{tmpl}_{pat}_{iter}_{arga}"
					outputs = run_rand(out, iter, pattern[1], arga)
					