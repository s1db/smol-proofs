from constraint import Constraint
from typing import Iterable, Dict
import copy
import logging


class Model:
    """
    The class for the model.
    """

    def __init__(self, filename, loud=False):
        name = filename.split('/')[-1].split('.')[0]
        self.loud = loud
        self.logger = logging.getLogger('model_logging')
        f_handler = logging.FileHandler('rup/'+name+'.rup', mode='w')
        f_handler.setLevel(logging.WARNING)
        self.logger.addHandler(f_handler)
        self.filename = filename
        self.model_constraint_db: Dict[int, Constraint] = {}
        self.proof_constraint_db: Dict[int, Constraint] = {}
        self.expected_no_of_literals = 0
        self.expected_no_of_constraints = 0
        self.literal_id_map = {}
        self.no_of_literals = 0
        self.no_of_constraints = 0
        self.no_of_model_constraints = 0
        self.constraints_known_to_propagate = set()
        self.dead_constraints = set()
        self.parse()

    def get_constraint(self, id) -> Constraint:
        """
        id: the id of the constraint to be returned
        """
        if id <= self.no_of_model_constraints:
            return self.model_constraint_db[id]
        else:
            return self.proof_constraint_db[id]

    def delete_constraint(self, id: int) -> None:
        """
        id: the id of the constraint to be deleted
        """
        if id <= self.no_of_model_constraints:
            del self.model_constraint_db[id]
        else:
            del self.proof_constraint_db[id]
        self.dead_constraints.add(id)

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
        if self.loud:
            print("    constraint " +"{:04d}".format(self.no_of_constraints) + " added: ", constraint)

    def constraint_parser(self, line: str) -> Constraint:
        """
        :param: line: the line to be parsed
        :return: the constraint object
        """
        line = line.strip()
        line = line[:-1].split(">=")
        degree = int(line[1])
        line = line[0].split()
        coefficients = [int(line[i]) for i in range(0, len(line), 2)]
        literals = [line[i] for i in range(1, len(line), 2)]
        literal_ids = []
        for i in literals:
            temp = i if i[0] != "~" else i[1:]
            if temp not in self.literal_id_map:
                self.no_of_literals += 1
                self.literal_id_map[temp] = self.no_of_literals
            literal_ids.append(
                self.literal_id_map[temp] if i[0] != "~" else -1*self.literal_id_map[temp])
        if len(coefficients) != len(literal_ids):
            raise Exception(
                "unequal number of literals and coefficients")
        temp = Constraint(literal_ids, coefficients, degree)
        print(temp)
        return temp

    def parse(self) -> None:
        """
        Parses the model file and adds the constraints to the model
        """
        with open(self.filename, mode="r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if "#variable=" in line:
                    temp = line.split()
                    self.expected_no_of_literals = int(temp[2])
                    self.expected_no_of_constraints = int(temp[4])
                if not line.startswith("*") and len(line) > 0:
                    temp = self.constraint_parser(line)
                    self.add_constraint(temp, True)
        self.no_of_model_constraints = self.no_of_constraints
        # if self.expected_no_of_literals != self.no_of_literals:
        #     print("WARNING: NUMBER OF LITERALS IN MODEL FILE HEADER DOES NOT MATCH WITH THE NUMBER OF LITERALS IN THE FILE")
        #     print("EXPECTED: ", self.expected_no_of_literals)
        #     print("ACTUAL: ", self.no_of_literals)
        #     print(list(self.literal_id_map.keys()))
        #     raise Exception(
        #         "NUMBER OF LITERALS IN MODEL FILE DOES NOT MATCH WITH THE NUMBER OF LITERALS IN THE CONSTRAINTS")
        if self.expected_no_of_constraints != self.no_of_constraints:
            print("WARNING: NUMBER OF CONSTRAINTS IN MODEL FILE DOES NOT MATCH WITH THE NUMBER OF CONSTRAINTS IN THE CONSTRAINTS")
            raise Exception(
                "NUMBER OF CONSTRAINTS IN MODEL FILE DOES NOT MATCH WITH THE NUMBER OF CONSTRAINTS IN THE CONSTRAINTS")
        if self.loud:
            print("NO OF LITERALS   : ", self.no_of_literals)
            print("NO OF CONSTRAINTS: ", self.no_of_constraints)

    def admit_v_step(self, line: str) -> None:
        """
        Checks if the passed solution is a valid solution
        """
        line = line.split()[1:]
        assignment = [self.literal_id_map[i] if i[0] != "~" else -1 *
                      self.literal_id_map[i[1:]] for i in line]
        new_constraint = Constraint([-i for i in assignment], [1 for i in assignment], 1, type="v")
        new_constraint.negation()
        if self.is_solution(new_constraint):
            new_constraint.negation()
            self.add_constraint(new_constraint)
        else:
            raise Exception("INVALID SOLUTION CLAIMED")
    def is_solution(self, constraint: Constraint):
        tau = constraint.propagate([])
        if self.loud:
            print("    ASSIGNMENT: ", tau)
        fired_constraints = []
        while True:
            unit_propagated = False
            for i in self.constraints_known_to_propagate:
                if i not in self.dead_constraints:
                    constraint = self.get_constraint(i)
                    constraint_propagates = constraint.propagate(tau)
                    if constraint_propagates != []:
                        fired_constraints.append(i)
                        tau += constraint_propagates
                        unit_propagated = True
                        break
            if not unit_propagated:
                for i in range(1, self.no_of_constraints+1):
                    if i not in self.constraints_known_to_propagate and i not in self.dead_constraints:
                        constraint = self.get_constraint(i)
                        constraint_propagates = constraint.propagate(tau)
                        if constraint_propagates != []:
                            fired_constraints.append(i)
                            tau += constraint_propagates
                            unit_propagated = True
                            break
            if not unit_propagated:
                if len(tau) != self.no_of_literals:
                    raise Exception(
                        "INVALID SOLUTION CLAIMED, NOT ALL VARIABLES ASSIGNED")
                else:
                    if self.loud:
                        print("    VALID SOLUTION FOUND")
                    self.logger.warning(str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                    return True

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
        _, antecedent, constraint_string = line[1:-1].split(" ", 2)
        antecedents = [int(antecedent)]
        constraint = self.constraint_parser(constraint_string)
        self.add_constraint(constraint)
        self.logger.warning(
            str(self.no_of_constraints)+":"+" ".join([str(i) for i in antecedents]))

    def admit_rup_step(self, line: str) -> None:
        """
        If the constraint is redundant, then it is added to the model.
        """
        print("LINE: ", line[1:-1])
        constraint = self.constraint_parser(line[1:-1])
        print("⭐", self.constraint_str(constraint))
        constraint.negation()
        print("⭐", self.constraint_str(constraint))
        if not self.rup(constraint):
            if self.loud:
                print("    RUP Failed -- cannot add constraint")
            raise Exception("RUP Failed -- Refutation Failed.")
        if self.loud: 
            print("    RUP Succeeded")
        constraint.negation()
        self.add_constraint(constraint)

    def rup(self, rup_constraint: Constraint) -> bool:
        """
        Returns True if the constraint is redundant to the model.
        Else returns False.
        """
        if self.loud:
            print("⭐", self.constraint_str(rup_constraint))
        tau = rup_constraint.propagate([])
        fired_constraints = []
        if self.loud:
            print("    ASSIGNMENT: ", tau)
        while True:
            unit_propagated = False
            for i in range(1, self.no_of_constraints+1):
                if i not in self.dead_constraints:
                    constraint = self.get_constraint(i)
                    if constraint.is_unsatisfied(tau):
                        fired_constraints.append(i)
                        if self.loud:
                            print("    FIRED CONSTRAINTS: ", fired_constraints)
                        self.logger.warning(
                            str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                        self.constraints_known_to_propagate.update(fired_constraints)
                        return True
            for i in self.constraints_known_to_propagate:
                if i not in self.dead_constraints:
                    constraint = self.get_constraint(i)
                    constraint_propagates = constraint.propagate(tau)
                    if constraint_propagates != []:
                        fired_constraints.append(i)
                        tau += constraint_propagates
                        unit_propagated = True
                        break
            if not unit_propagated:
                for i in range(1, self.no_of_constraints+1):
                    if i not in self.constraints_known_to_propagate and i not in self.dead_constraints:
                        constraint = self.get_constraint(i)
                        constraint_propagates = constraint.propagate(tau)
                        if constraint_propagates != []:
                            fired_constraints.append(i)
                            tau += constraint_propagates
                            unit_propagated = True
                            break
            if not unit_propagated:
                return False
    def constraint_str(self, constraint:Constraint) -> str:
        """
        Returns the string representation of the constraint
        """
        id_literal_map = {v: k for k, v in self.literal_id_map.items()}
        constraint_string = ""
        for i in constraint.literals:
            if i < 0:
                constraint_string += " "+ str(constraint.coefficients[abs(i)]) + " ~" + str(id_literal_map[abs(i)])
            else:
                constraint_string += " "+ str(constraint.coefficients[abs(i)]) + " " + str(id_literal_map[abs(i)])
        constraint_string += " >= "
        constraint_string += str(constraint.degree)
        return constraint_string
    def admit_check_contradiction(self, line: str) -> None:
        """
        Checks if the given contradiction is a contradiction
        """
        contradiction_id = int(line.split()[1])
        if self.get_constraint(contradiction_id).is_unsatisfied([]):
            if self.loud:
                print("Contradiction Found")
        else:
            if self.loud:
                print("Incorrect Contradiction Claimed")
