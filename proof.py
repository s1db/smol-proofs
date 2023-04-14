from model import Model
from collections import defaultdict
import logging
# pylint: disable=R0903
class Proof:
    """
    Class to parse a proof file and admit the steps to the model
    """

    def __init__(self, file, loud=False):
        self.proof_file = file + '.veripb'
        self.model = Model(file + '.opb', loud=loud)
        self.no_of_formulas = self.model.no_of_constraints
        self.loud = loud
        self.parse()

    def parse(self):
        """
        Parses the proof file and admits the steps to the model
        """
        wipeout = defaultdict(set)
        active_level = 0
        with open(self.proof_file, mode="r", encoding="utf-8") as file:
            for line in file:
                if line[0] == '*':
                    if self.loud:
                        print("COMMENT: ", line[:-1])
                if line[0] == '#':
                    line = line[1:].split()
                    lvl = int(line[0])
                    wipeout[lvl]
                    active_level = lvl
                    if self.loud:
                        print("LEVEL SET: ", lvl)
                elif line.startswith("pseudo"):
                    if self.loud:
                        print("FILE TYPE: ", line)
                elif line[0] == 'f':
                    if self.loud:
                        print("FORMULA CHECK: ", line)
                    file = int(line.split()[1])
                    if isinstance(file, int):
                        if file != self.no_of_formulas:
                            raise ValueError("Number of formulas mismatch")
                elif line[0] == 'p':
                    if self.loud:
                        print("POL STEP: ", line[:-1])
                    self.model.admit_pol_step(line)
                    wipeout[active_level].add(self.model.no_of_constraints)
                elif line[0] == 'u':
                    if self.loud:
                        print("RUP STEP: ", line[:-1])
                    self.model.admit_rup_step(line)
                elif line[0] == 'j':
                    if self.loud:
                        print("J STEP: ", line[:-1])
                    self.model.admit_j_step(line)
                elif line[0] == 'v':
                    if self.loud:
                        print("V STEP: ", line[:-1])
                    self.model.admit_v_step(line)
                elif line[0] == 'c':
                    self.model.admit_check_contradiction(line)
                elif line[0] == 'w':
                    lvl = int(line.split()[1])
                    to_delete = set()
                    # if self.loud:
                    #     print("WIPING OUT LEVELS: ", lvl)
                    # print(wipeout)
                    # for i in wipeout.keys():
                    #     if i >= lvl:
                    #         to_delete |= wipeout[i]
                    #         wipeout[i] = set()
                    # print("deleting: ", to_delete)
                    # for i in to_delete:
                    #     self.model.delete_constraint(i)
        logging.shutdown()


if "__main__" == __name__:
    FILE = "magic_series_20"
    DIR = "magic_series_proofs/"
    proof = Proof(DIR+FILE, loud=True)
