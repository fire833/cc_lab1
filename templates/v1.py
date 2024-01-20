
template = """
#include <stdlib.h>
#include <string.h>

const int mult_pairs = {{ mult_pairs }};
const int arg_count = {{ arg_count }};

int *parse_input(char* input) {
	return (int *)malloc(5);
}

void compute(int n, int *input, float *output) {
	for (int i = 0; i < n; i++) {
		output[i] = {% for sum in sums %}({% for value in sum %}input[i+{{ value }}]{% if not sum|last == value %}+{% endif %}{% endfor %}){% if not sums|last == sum %}*{% endif %}{% endfor %};
	}
}

int main(int argc, char **argv) {
	int *input = parse_input(argv[1]);
	float len = sizeof(*input) / sizeof(int);

	float *output;
	output = (float*)malloc(sizeof(float) * (int)(arg_count / len));

	compute(mult_pairs / len, input, output);
}
"""
