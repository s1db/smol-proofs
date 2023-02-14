import re
import io

def parse_pol_step(line):
    return line.split()[1:-1]

def parse_rup_step(line):
    return line.split()[1:-1]

def parse_imply_add_step(line):
    return line.split()[2:-1]

def run_parser(input_file):
    # Parse the input file and return a list of constraints
    no_of_formulas = 0
    proof_db = {}
    f = io.open(input_file, 'r')
    for line in f.readlines():
        # proof in veripb version
        if line == 'pseudo-Boolean proof version 1.0\n':
            # print("--version--")
            continue
        # comment
        elif line[0] == '*':
            # print("--comment--")
            continue
        # number of formulas in formula file, can be useful to assert.
        elif line[0] == 'f':
            m = int(line.split()[1])
            if type(m) == int:
                no_of_formulas = m
                # print("--no_of_formulas--", no_of_formulas)
            else:
                raise ValueError('Invalid formula line: %s' % line)
        elif line[0] == '#':
            pass
        elif line[0] == 'u':
            no_of_formulas += 1
            print(str(no_of_formulas)+ ": " + " ".join(parse_pol_step(line)))
            proof_db[no_of_formulas] = parse_pol_step(line)
        elif line[0] == 'j':
            # parses the line and adds the constraint to the formula db.
            # TODO: do the implication 
            no_of_formulas += 1
            print(str(no_of_formulas)+ ": " + " ".join(parse_pol_step(line)))
            proof_db[no_of_formulas] = parse_pol_step(line)
        elif line[0] == 'p':
            no_of_formulas += 1
            print(str(no_of_formulas)+ ": " + " ".join(parse_pol_step(line)))
            proof_db[no_of_formulas] = parse_pol_step(line)
    return proof_db

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: %s input_file' % sys.argv[0])
        sys.exit(1)
    input_file = sys.argv[1]
    proof = run_parser(input_file)
