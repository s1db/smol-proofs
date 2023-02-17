from typing import Iterable, Dict
from collections import defaultdict
import copy
from math import ceil
import logging


class PBConstraint:
    def __init__(self, literals, coefficients, degree):
        self.literals = set(literals)
        self.coefficients = defaultdict(int)
        self.degree = degree  # of falsity
        self.no_of_literals = len(self.literals)
        for literal, coefficient in zip(literals, coefficients):
            self.coefficients[literal] += coefficient
        if self.no_of_literals != len(self.coefficients):
            raise Exception("unequal number of literals and coefficients.")

    def is_unsatisfied(self, assignment: Iterable) -> bool:
        """
        :param: assignment: the assignment
        :return: True if the constraint is satisfied in the `assignment`,
            i.e. one of its literals is True.
        """
        return self.slack(assignment) < 0

    def flip_literal(self, literal):
        """
        Changes the sign of the literal in the constraint.
        """
        coefficient = self.coefficients[literal]
        self.degree -= coefficient
        self.coefficients[-literal] += -coefficient
        del self.coefficients[literal]
        self.literals.add(-literal)
        self.literals.remove(literal)

    def delete_literal(self, literal):
        """
        Deletes the literal and/or the negative of the literal from the constraint.
        """
        literals = self.literals
        if literal in literals:
            self.literals.remove(literal)
        if -literal in literals:
            self.literals.remove(-literal)
        if literal in self.coefficients:
            del self.coefficients[literal]
        if -literal in self.coefficients:
            del self.coefficients[-literal]

    def literal_normalized_form(self):
        """
        Normalizes the constraint in literal normalized form.
        """
        literals = list(self.literals)
        for i in literals:
            if i < 0:
                self.flip_literal(i)
            if i in self.coefficients and self.coefficients[i] == 0:
                self.delete_literal(i)

    def coefficient_normalized_form(self):
        """
        Normalizes the constraint in coefficient normalized form.
        """
        literals = list(self.literals)
        for i in literals:
            coefficient = self.coefficients[i]
            if coefficient < 0:
                self.flip_literal(i)
            if i in self.coefficients and self.coefficients[i] == 0:
                self.delete_literal(i)

    def slack(self, assignment: Iterable) -> int:
        """
        :param: assignment: the assignment
        :return: the slack of the constraint in the `assignment`,
            i.e. the number of literals not falsified by an
            assignment minus the degree.
        """
        temp = 0
        for i in self.literals:
            if -i not in assignment:
                temp += self.coefficients[i]
        temp -= self.degree
        return temp

    def propagate(self, assignment: Iterable) -> Iterable:
        """
        :param: assignment: the assignment
        :return: the literals that need be added to the assignment to satisfy the constraint.
        """

        need_to_be_true = []
        slack = self.slack(assignment)
        for i in self.literals:
            # if any assignment is falsified, skip it.
            if not (-i in assignment or i in assignment):
                if slack < self.coefficients[i]:
                    need_to_be_true.append(i)
        return need_to_be_true

    def negation(self):
        """
        Negates the constraint
        """
        for i in self.literals:
            self.coefficients[i] = - self.coefficients[i]
        self.degree = -self.degree + 1
        self.coefficient_normalized_form()

    def implies(self, constraint) -> int:
        """
        TODO: check if self semantically implies other constraint
        :param: constraint
        :return: True if self semantically implies other constraint
        """
        weaken_cost = 0
        for i in constraint.literals:
            if i not in self.literals:
                return False
            else:
                if self.coefficients[i] < constraint.coefficients[i]:
                    return False
                else:
                    weaken_cost += self.coefficients[i] - \
                        constraint.coefficients[i]
        if self.degree < constraint.degree:
            return False
        else:
            weaken_cost += self.degree - constraint.degree
        return weaken_cost

    def saturation(self):
        for i in self.literals:
            self.coefficients[i] = min(self.coefficients[i], self.degree)

    @staticmethod
    def multiply(constraint, constant):
        """
        multiplies a constraint by a constraint.
        """
        for i in constraint.literals:
            constraint.coefficients[i] = constraint.coefficients[i] * constant
        constraint.degree = constraint.degree * constant
        constraint.coefficient_normalized_form()
        return constraint

    @staticmethod
    def add(constraint1, constraint2):
        """
        Adds constraint 1 and 2.
        """
        new_constraint = copy.deepcopy(constraint1)
        new_constraint.literal_normalized_form()
        constraint2.literal_normalized_form()
        for i in constraint2.literals:
            if i not in new_constraint.literals:
                new_constraint.literals.add(i)
            new_constraint.coefficients[i] += constraint2.coefficients[i]
        new_constraint.degree += constraint2.degree
        constraint2.coefficient_normalized_form()
        new_constraint.coefficient_normalized_form()
        return new_constraint

    @staticmethod
    def subtract(constraint1, constraint2):
        """
        returns the subtraction of constraint 2 from constraint 1.
        """
        new_constraint = copy.deepcopy(constraint1)
        for i in constraint2.literals:
            new_constraint.coefficients[i] -= constraint2.coefficients[i]
        new_constraint.degree -= constraint2.degree
        new_constraint.coefficient_normalized_form()
        return new_constraint

    @staticmethod
    def divide(constraint1, constant):
        """
        :param: constraint1: the constraint to be divided
        :param: constant: the constant to divide the constraint by
        :return: the constraint divided by the constant"""
        new_constraint = copy.deepcopy(constraint1)
        for i in new_constraint.literals:
            new_constraint.coefficients[i] = ceil(
                new_constraint.coefficients[i] / constant)
        new_constraint.degree = ceil(new_constraint.degree / constant)
        new_constraint.coefficient_normalized_form()
        return new_constraint

    def __str__(self) -> str:
        """
        :return: the string representation of the constraint.
        """
        temp = ""
        abs_sorted_lits = sorted(list(self.literals), key=abs)
        for i in abs_sorted_lits:
            if i > 0:
                temp += str(self.coefficients[i]) + " x" + str(i) + " "
            else:
                temp += str(self.coefficients[i]) + " ~x" + str(-i) + " "
        temp = temp[:-1] + " >= " + str(self.degree)
        return temp


class PBModel:
    """
    The class for the model.
    """

    def __init__(self, filename):
        name = filename.split('/')[-1].split('.')[0]
        self.logger = logging.getLogger('model_logging')
        f_handler = logging.FileHandler(name+'.rup', mode='w')
        f_handler.setLevel(logging.WARNING)
        self.logger.addHandler(f_handler)
        self.filename = filename
        self.constraint_db: Dict[str, PBConstraint] = {}
        self.no_of_variables = 0
        self.no_of_constraints = 0
        self.parse()

    def add_constraint(self, constraint: PBConstraint) -> None:
        """
        :param: constraint: the constraint to be added
        :return: None
        Adds the constraint to the model and updates
        the number of constraints
        """
        self.no_of_constraints += 1
        constraint.coefficient_normalized_form()
        self.constraint_db[self.no_of_constraints] = constraint
        print("    constraint " +
              "{:04d}".format(self.no_of_constraints) + " added: ", constraint)
        # convert the line above in a fstring format

    def constraint_parser(self, line: str) -> PBConstraint:
        """
        :param: line: the line to be parsed
        :return: the constraint object
        """
        line = line[:-1].split(">=")
        degree = int(line[1])
        line = line[0].split()
        coefficients = [int(line[i])
                        for i in range(0, len(line), 2)]
        literals = [int(line[i][1:]) if line[i][0] != "~" else -
                    1*int(line[i][2:]) for i in range(1, len(line), 2)]
        if len(coefficients) != len(literals):
            raise Exception(
                "unequal number of literals and coefficients")
        temp = PBConstraint(literals, coefficients, degree)
        self.no_of_variables += len(literals)
        return temp

    def parse(self) -> None:
        """
        Parses the model file and adds the constraints to the model
        """
        with open(self.filename, mode="r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line.startswith("*") and len(line) > 0:
                    temp = self.constraint_parser(line)
                    self.add_constraint(temp)
        print("\nMODEL PARSED -- NO OF CONSTRAINTS: ", self.no_of_constraints)

    def admit_pol_step(self, statement: str) -> None:
        """
        Processes the polish notation statement on the constraints
        and adds the new constraint to the model
        """
        statement = statement.split(" ")[1:-1]
        ancedents = []
        stack = []
        operations = ["+", "-", "*", "/"]
        if len(statement) == 1:
            temp = copy.deepcopy(self.constraint_db[int(statement[0])])
            stack.append(temp)
        for i in statement:
            if i not in operations:
                ancedents.append(int(i))
                temp = copy.deepcopy(self.constraint_db[int(i)])
                stack.append(temp)
            else:
                constraint_1 = stack.pop()
                constraint_2 = stack.pop()
                temp = None
                if i == '+':
                    temp = PBConstraint.add(constraint_1, constraint_2)
                if i == '-':
                    temp = PBConstraint.subtract(constraint_1, constraint_2)
                if i == '*':
                    raise NotImplementedError(
                        "multiplication is not yet implemented")
                    # temp = PBConstraint.multiply(self.constraint_db[a], b)
                if i == '/':
                    raise NotImplementedError(
                        "division is not yet implemented")
                    # temp = PBConstraint.divide(self.constraint_db[a], b)
                stack.append(temp)
        self.logger.warning(
            str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in ancedents]))
        self.add_constraint(stack.pop())

    def admit_j_step(self, line: str) -> None:
        """
        Adds the implication constraint to the model
        """
        # constraint = self.constraint_parser(line[1:-1])
        line = line[:-1].split(">=")
        degree = int(line[1][:-1])
        line = line[0].split()
        # print(line)
        ancedents = [int(line[1])]
        line = line[2:]
        coefficients = [int(line[i])
                        for i in range(0, len(line), 2)]
        literals = [int(line[i][1:]) if line[i][0] != "~" else -
                    1*int(line[i][2:]) for i in range(1, len(line), 2)]
        if len(coefficients) != len(literals):
            raise Exception(
                "unequal number of literals and coefficients")
        temp = PBConstraint(literals, coefficients, degree)
        self.logger.warning(
            str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in ancedents]))
        self.add_constraint(temp)

    def admit_rup_step(self, line: str) -> None:
        """
        If the constraint is redundant, then it is added to the model.
        """
        constraint = self.constraint_parser(line[1:-1])
        constraint.negation()
        if not self.rup(constraint):
            print("    RUP Failed -- cannot add constraint")
            raise Exception("RUP Failed -- Refutation Failed.")
        print("    RUP Succeeded")
        constraint.negation()
        self.add_constraint(constraint)

    def rup(self, rup_constraint: PBConstraint) -> bool:
        """
        Returns True if the constraint is redundant to the model.
        Else returns False.
        """
        tau = rup_constraint.propagate([])
        fired_constraints = []
        print("    ASSIGNMENT: ", tau)
        while True:
            unit_propagated = False
            for constraint_id, constraint in self.constraint_db.items():
                if constraint.is_unsatisfied(tau):
                    fired_constraints.append(constraint_id)
                    print("    FIRED CONSTRAINTS: ", fired_constraints)
                    self.logger.warning(
                        str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                    return True
            for constraint_id, constraint in self.constraint_db.items():
                constraint_propagates = constraint.propagate(tau)
                if constraint_propagates != []:
                    fired_constraints.append(constraint_id)
                    tau += constraint_propagates
                    unit_propagated = True
                    break
            if not unit_propagated:
                return False

    def admit_check_contradiction(self, line: str) -> None:
        """
        Checks if the given contradiction is a contradiction
        """
        contradiction_id = int(line.split()[1])
        if self.constraint_db[contradiction_id].is_unsatisfied([]):
            print("Contradiction Found")
        else:
            print("Incorrect Contradiction Claimed")


# pylint: disable=R0903
class PBProof:
    """
    Class to parse a proof file and admit the steps to the model
    """

    def __init__(self, model_file, proof_file):
        self.proof_file = proof_file
        self.model = PBModel(model_file)
        self.no_of_formulas = self.model.no_of_constraints
        self.parse()

    def parse(self):
        """
        Parses the proof file and admits the steps to the model
        """
        with open(self.proof_file, mode="r", encoding="utf-8") as file:
            for line in file:
                if line[0] == '#':
                    # print("COMMENT: ", line[:-1])
                    pass
                elif line.startswith("pseudo"):
                    print("FILE TYPE: ", line)
                elif line[0] == 'f':
                    print("FORMULA CHECK: ", line)
                    file = int(line.split()[1])
                    if isinstance(file, int):
                        if file != self.no_of_formulas:
                            raise ValueError("Number of formulas mismatch")
                elif line[0] == 'p':
                    print("POL STEP: ", line[:-1])
                    self.model.admit_pol_step(line)
                elif line[0] == 'u':
                    print("RUP STEP: ", line[:-1])
                    self.model.admit_rup_step(line)
                elif line[0] == 'j':
                    print("J STEP: ", line[:-1])
                    self.model.admit_j_step(line)
                elif line[0] == 'c':
                    self.model.admit_check_contradiction(line)


if "__main__" == __name__:
    proof = PBProof('proofs/proof.opb', 'proofs/proof.pbp')
