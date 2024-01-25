import subprocess

TESTS = [[21, ["1,2", "3,4"]]]

def test(target, input):
    # Run python compiler
    py_comp = ["python", "meta.py"] + input
    py_comp_res = subprocess.run(py_comp, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check python compiler errors
    if py_comp_res.returncode != 0:
        print(py_comp_res.stderr.decode().strip())

    # Compile the generated C program
    c_comp = ["gcc", "prog.c", "-o", "prog.exe"]
    c_comp_res = subprocess.run(c_comp, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check generated C program compiler errors
    if c_comp_res.returncode != 0:
        print(c_comp_res.stderr.decode().strip())

    # Run the generated executable
    run_exe = ["./prog.exe"]
    run_exe_res = subprocess.run(run_exe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check values
    actual = run_exe_res.stdout.decode().strip()
    if actual == target:
        print("Test Completed: Success")
    else:
        print(f'Test failed:\n\tTarget: {target}\n\tActual: {actual}')

if __name__ == '__main__':
    for t in TESTS:
        test(t[0], t[1])