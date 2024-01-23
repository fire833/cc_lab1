
template = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int mult_pairs = {{ mult_pairs }};
const int arg_count = {{ arg_count }};

int *parse_input(char* input, int len) {
	int index = 0;
	int *output = (int *)malloc(((len + 1) / 2) * sizeof(int));
	int sum = 0;

	for (int i = 0; i < len; i++) {
    	// Shift over the sum and add a new value, whatever it may be.
    	switch (input[i]) {
    	case '0':
      		sum = 10 * sum;
			continue;
    	case '1':
      		sum = 10 * sum + 1;
			continue;
    	case '2':
      		sum = 10 * sum + 2;
			continue;
    	case '3':
      		sum = 10 * sum + 3;
			continue;
    	case '4':
      		sum = 10 * sum + 4;
			continue;
    	case '5':
      		sum = 10 * sum + 5;
			continue;
    	case '6':
      		sum = 10 * sum + 6;
			continue;
    	case '7':
      		sum = 10 * sum + 7;
			continue;
    	case '8':
      		sum = 10 * sum + 8;
			continue;
    	case '9':
      		sum = 10 * sum + 9;
			continue;

    	// We are at the end of the number, reset to a new sum.
    	case ',': {
      		output[index] = sum;
      		sum = 0;
      		index++;
			continue;
    	}
    	// We are at the end of a line, return immediately.
    	case '\\n' | EOF: {
      		output[index] = sum;
      		sum = 0;
      		index++;
      		break;
    	} }
  	}

	return output;
}

void compute(int n, int *input, int *output) {
	for (int i = 0; i < n; i++) {
		output[i] = {% for sum in sums %}({% for value in sum %}input[i+{{ value }}]{% if not sum|last == value %}+{% endif %}{% endfor %}){% if not sums|last == sum %}*{% endif %}{% endfor %};
	}
}

int main(int argc, char **argv) {
	if (argc != 2) {
		printf("2 arguments are required, the program call name and the list of values, comma separated.");
		exit(1);
	}

	char *values = argv[1];
	int value_length = strlen(values);

	if (value_length % arg_count != 0) {
		printf("must have an even multiple of values to %d arguments", arg_count);
		exit(1);
	}

	int *input = parse_input(values);
	int input_len = (value_length / 2) + 1;

	int *output;
	int output_len = (len - arg_count + 1);
	output = (int*)malloc(output_len * sizeof(int));

	compute(input_len, input, output);

	for (int i = 0; i < output_len; i++) {
    	printf("%d ", output[i]);
  	}

	free(input);
	free(output);
}
"""
