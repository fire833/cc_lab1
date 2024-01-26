
from argparse import ArgumentParser
from templates.v1 import template as v1tmpl

def new_parser():
	p = ArgumentParser(description="Wrapper scripts/utilities for Lab 1 Metaprogramming", add_help=True, allow_abbrev=True)
	sub = p.add_subparsers()

	generate = sub.add_parser("generate")
	generate.set_defaults(func=generate)
	generate.add_argument("--pattern", help="Provide the pattern you want to generate against (should be a string with spaces)", type=str)
	generate.add_argument("--template", help="Provide the template you want to generate from, current values are (v1)", type=str, default="v1")
	generate.add_argument("--output", help="Provide the output location of the generated program.", type=str, default="./prog.c")
	run = sub.add_parser("run")
	run.set_defaults(func=run)

	return p

templates = {
	"v1": v1tmpl,
}

def generate(pattern, template, output):
	print("generating new output program")

	if templates[template]:
		values = []
		arg_count = 0

		values.append([int(arg) for arg in pattern.split(",")])

		for outer in values:
			for v in outer:
				arg_count += 1

		mult_pairs = len(values)

		env = jinja2.Environment()
		t = env.from_string(templates[template])
		f = open(file=output, mode="w")
		f.write(t.render(mult_pairs=mult_pairs, arg_count=arg_count, sums=values))
		f.close()

def run():
	pass