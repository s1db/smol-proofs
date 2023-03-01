from constraint import Constraint
from typing import Iterable, Dict
import copy
import logging


class Model:
    """
    The class for the model.
    """

    def __init__(self, filename):
        name = filename.split('/')[-1].split('.')[0]
        self.logger = logging.getLogger('model_logging')
        f_handler = logging.FileHandler('rup/'+name+'.rup', mode='w')
        f_handler.setLevel(logging.WARNING)
        self.logger.addHandler(f_handler)
        self.filename = filename
        self.model_constraint_db: Dict[int, Constraint] = {}
        self.proof_constraint_db: Dict[int, Constraint] = {}
        self.no_of_variables = 0
        self.no_of_constraints = 0
        self.no_of_model_constraints = 0
        self.parse()

    def get_constraint(self, id) -> Constraint:
        """
        id: the id of the constraint to be returned
        """
        # print(self.model_constraint_db.keys())
        # print(self.no_of_model_constraints, id)
        if id <= self.no_of_model_constraints:
            return self.model_constraint_db[id]
        else:
            return self.proof_constraint_db[id]

    def add_constraint(self, constraint: Constraint, to_model=False) -> None:
        """
        :param: constraint: the constraint to be added
        :return: None
        Adds the constraint to the model and updates
        the number of constraints
        """
        self.no_of_constraints += 1
        if to_model:
            self.model_constraint_db[self.no_of_constraints] = constraint
        else:
            self.proof_constraint_db[self.no_of_constraints] = constraint
        print("    constraint " +
              "{:04d}".format(self.no_of_constraints) + " added: ", constraint)

    def constraint_parser(self, line: str) -> Constraint:
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
        temp = Constraint(literals, coefficients, degree)
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
                    self.add_constraint(temp, True)
        self.no_of_model_constraints = self.no_of_constraints
        print("\nMODEL PARSED -- NO OF CONSTRAINTS: ", self.no_of_constraints)

    def admit_v_step(self, line: str) -> None:
        """
        Checks if the passed solution is a valid solution
        """
        line = line.split()
        assignment = [int(i[1:]) if i[0] != "~" else -1 *
                      int(line[i][2:]) for i in line]
        tau = assignment
        fired_constraints = []
        print("    ASSIGNMENT: ", tau)
        while True:
            unit_propagated = False
            for constraint_id, constraint in self.proof_constraint_db.items():
                if constraint.is_unsatisfied(tau):
                    raise Exception(
                        "INVALID SOLUTION CLAIMED, FALSIFYING CONSTRAINT: " + str(constraint_id))

            for constraint_id, constraint in self.model_constraint_db.items():
                if constraint.is_unsatisfied(tau):
                    raise Exception(
                        "INVALID SOLUTION CLAIMED, FALSIFYING CONSTRAINT: " + str(constraint_id))

            for constraint_id, constraint in self.proof_constraint_db.items():
                constraint_propagates = constraint.propagate(tau)
                if constraint_propagates != []:
                    fired_constraints.append(constraint_id)
                    tau += constraint_propagates
                    unit_propagated = True
                    break
            if not unit_propagated:
                for constraint_id, constraint in self.model_constraint_db.items():
                    constraint_propagates = constraint.propagate(tau)
                    if constraint_propagates != []:
                        fired_constraints.append(constraint_id)
                        tau += constraint_propagates
                        unit_propagated = True
                        break
            if not unit_propagated:
                if len(tau) != self.no_of_variables:
                    raise Exception(
                        "INVALID SOLUTION CLAIMED, NOT ALL VARIABLES ASSIGNED")
                else:
                    new_constraint = Constraint(
                        [-i for i in assignment], [1 for i in assignment], 1)
                    self.add_constraint(new_constraint)

    def admit_pol_step(self, statement: str) -> None:
        """
        Processes the polish notation statement on the constraints
        and adds the new constraint to the model
        """
        statement = statement.split(" ")[1:-1]
        antecedents = []
        stack = []
        operations = ["+", "-", "*", "/"]
        if len(statement) == 1:
            id = int(statement[0])
            temp = copy.deepcopy(self.get_constraint(id))
            stack.append(temp)
        for i in statement:
            if i not in operations:
                antecedents.append(int(i))
                temp = copy.deepcopy(self.get_constraint(int(i)))
                stack.append(temp)
            else:
                constraint_1 = stack.pop()
                constraint_2 = stack.pop()
                temp = None
                if i == '+':
                    temp = constraint_1 + constraint_2
                if i == '-':
                    temp = constraint_1 - constraint_2
                if i == '*':
                    temp = constraint_1 * constraint_2
                if i == '/':
                    temp = constraint_1 / constraint_2
                stack.append(temp)
        self.logger.warning(
            str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in antecedents]))
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
        antecedents = [int(line[1])]
        line = line[2:]
        coefficients = [int(line[i])
                        for i in range(0, len(line), 2)]
        literals = [int(line[i][1:]) if line[i][0] != "~" else -
                    1*int(line[i][2:]) for i in range(1, len(line), 2)]
        if len(coefficients) != len(literals):
            raise Exception(
                "unequal number of literals and coefficients")
        temp = Constraint(literals, coefficients, degree)
        self.logger.warning(
            str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in antecedents]))
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

    def rup(self, rup_constraint: Constraint) -> bool:
        """
        Returns True if the constraint is redundant to the model.
        Else returns False.
        """
        tau = rup_constraint.propagate([])
        fired_constraints = []
        print("    ASSIGNMENT: ", tau)
        while True:
            unit_propagated = False
            for constraint_id, constraint in self.proof_constraint_db.items():
                if constraint.is_unsatisfied(tau):
                    fired_constraints.append(constraint_id)
                    print("    FIRED CONSTRAINTS: ", fired_constraints)
                    self.logger.warning(
                        str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                    return True
            for constraint_id, constraint in self.model_constraint_db.items():
                if constraint.is_unsatisfied(tau):
                    fired_constraints.append(constraint_id)
                    print("    FIRED CONSTRAINTS: ", fired_constraints)
                    self.logger.warning(
                        str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                    return True
            for constraint_id, constraint in self.proof_constraint_db.items():
                constraint_propagates = constraint.propagate(tau)
                if constraint_propagates != []:
                    fired_constraints.append(constraint_id)
                    tau += constraint_propagates
                    unit_propagated = True
                    break
            if not unit_propagated:
                for constraint_id, constraint in self.model_constraint_db.items():
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
        if self.get_constraint(contradiction_id).is_unsatisfied([]):
            print("Contradiction Found")
        else:
            print("Incorrect Contradiction Claimed")
