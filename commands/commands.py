
from argparse import ArgumentParser
from templates.v1 import template as v1tmpl
import jinja2
import sys
import subprocess
import os
import random

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


	return p

def runner(args: ArgumentParser):
	# print(args)
	if sys.argv[1] == "generate":
		print("generating new output program")
		return generate(args.pattern, args.template, args.outputs, args.output, args.compiler, True)
	elif sys.argv[1] == "run":
		print("running output program")
		return run(args.input, [int(arg) for arg in args.values.split(",")])
	elif sys.argv[1] == "runrand":
		print("running output program with random inputs")
		return run_rand(args.input, args.iterations, args.argc, args.arga)

templates = {
	"v1": v1tmpl,
}

def generate(pattern: str, template: str, outputs: str, output: str, compiler: str, asm: bool):
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
		f = open(file=output, mode="w")
		f.write(t.render(mult_pairs=mult_pairs, arg_count=arg_count, sums=values))
		f.close()
		
		subprocess.run([compiler, "-O3", "-Wall", "-o", output, outputs])
		if asm:
			subprocess.run([compiler, "-S", "-O3", "-Wall", "-o", f"{output}.S", outputs])
	else:
		print("please specify a valid template to use")

def run(input: str, args: [int]):
	parsed = ""

	for i in args:
		parsed += f"{i},"

	return subprocess.run([input, str(len(args)), parsed.rstrip(",")])

def run_rand(input: str, iterations: int, arg_count: int, additional_args: int):
	s = arg_count + additional_args
	for i in range(iterations):
		run(input, [int(random.randint(1,1000)) for i in range(s)])
