
from argparse import ArgumentParser
from templates.v1 import template as v1tmpl
import jinja2
import sys
import subprocess

def new_parser():
	p = ArgumentParser(prog=sys.argv[0], description="Wrapper scripts/utilities for Lab 1 Metaprogramming", add_help=True, allow_abbrev=True)
	sub = p.add_subparsers(title="subcommands")

	generate = sub.add_parser("generate")
	generate.add_argument("--pattern", help="Provide the pattern you want to generate against (should be a string with spaces)", type=str, dest="pattern")
	generate.add_argument("--template", help="Provide the template you want to generate from, current values are (v1)", type=str, default="v1", dest="template")
	generate.add_argument("--outputs", help="Provide the output location of the generated program source.", type=str, default="./prog.c", dest="outputs")
	generate.add_argument("--output", help="Provide the output location of the generated program executable.", type=str, default="./prog", dest="output")
	generate.set_defaults(func=generate)
	run = sub.add_parser("run")
	run.set_defaults(func=run)

	return p

def runner(args: ArgumentParser):
	# print(args)
	if sys.argv[1] == "generate":
		return generate(args.pattern, args.template, args.outputs, args.output, True)
	elif sys.argv[1] == "run":
		return run(args.asm)

templates = {
	"v1": v1tmpl,
}

def generate(pattern: str, template: str, outputs: str, output: str, asm: bool):
	print("generating new output program")

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
		
		subprocess.run(["gcc", "-O3", "-Wall", "-o", output, outputs])
		if asm:
			subprocess.run(["gcc", "-S", "-O3", "-Wall", "-o", f"{output}.S", outputs])

def run():
	print("running output program")
	pass