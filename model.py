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
        # print(id)
        if id <= self.no_of_model_constraints:
            return self.model_constraint_db[id]
        else:
            return self.proof_constraint_db[id]

    def delete_constraint(self, id: int) -> None:
        """
        id: the id of the constraint to be deleted
        """
        if id <= self.no_of_model_constraints:
            raise ValueError("Cannot delete a constraint from the proof")
            # del self.model_constraint_db[id]
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
            print("    ConstraintId " +"{:03d}".format(self.no_of_constraints) + ":", self.constraint_str(constraint))

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
        # if self.expected_no_of_constraints != self.no_of_constraints:
        #     print("WARNING: NUMBER OF CONSTRAINTS IN MODEL FILE DOES NOT MATCH WITH THE NUMBER OF CONSTRAINTS IN THE CONSTRAINTS")
        #     raise Exception(
        #         "NUMBER OF CONSTRAINTS IN MODEL FILE DOES NOT MATCH WITH THE NUMBER OF CONSTRAINTS IN THE CONSTRAINTS")
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
        statement = statement.strip().split(" ")[1:-1]
        antecedents = []
        stack = []
        operations = ["+", "-", "*", "d"]
        if len(statement) == 1:
            id = int(statement[0])
            stack.append(id)
        if self.loud:
            print(statement)
        for i in range(len(statement)):
            if self.loud:
                print("    ", statement[i], stack)
            if statement[i] not in operations:
                id = statement[i]
                stack.append(id)
            else:
                temp = None
                if statement[i] == '+':
                    # print("ADDING CONSTRAINT")
                    constraint_2 = stack.pop()
                    if not isinstance(constraint_2, Constraint):
                        # print(constraint_2, "CONSTRAINT 2 IS NOT A CONSTRAINT")
                        if constraint_2.isdigit():
                            # print(constraint_2)
                            # print("CONSTRAINT 2 IS A DIGIT")
                            antecedents.append(int(constraint_2))
                            constraint_2 = self.get_constraint(int(constraint_2))
                        else:
                            # print("CONSTRAINT 2 IS A LITERAL")
                            if constraint_2[0] == "~":
                                constraint_2 = Constraint([-self.literal_id_map[constraint_2[1:]]], [1], 0)
                            else:
                                constraint_2 = Constraint([self.literal_id_map[constraint_2]], [1], 0)
                    constraint_1 = stack.pop()
                    # print(constraint_1)
                    if not isinstance(constraint_1, Constraint):
                        # print(constraint_1, "CONSTRAINT 1 IS NOT A CONSTRAINT")
                        if constraint_1.isdigit():
                            # print(constraint_1, "CONSTRAINT 1 IS A DIGIT")
                            antecedents.append(int(constraint_1))
                            constraint_1 = self.get_constraint(int(constraint_1))
                        else:
                            if constraint_1[0] == "~":
                                constraint_1 = Constraint([-self.literal_id_map[constraint_1[1:]]], [1], 0)
                            else:
                                constraint_1 = Constraint([self.literal_id_map[constraint_1]], [1], 0)
                    temp = constraint_1 + constraint_2
                    # if self.loud:
                    #     print("adding", constraint_1, constraint_2, temp)
                elif statement[i] == '-':
                    constraint_2 = stack.pop()
                    if not isinstance(constraint_2, Constraint):
                        if constraint_2.isdigit():
                            constraint_2 = self.get_constraint(int(constraint_2))
                        else:
                            if constraint_2[0] == "~":
                                constraint_2 = Constraint([-self.literal_id_map[constraint_2[1:]]], [1], 0)
                            else:
                                constraint_2 = Constraint([self.literal_id_map[constraint_2]], [1], 0)
                    constraint_1 = stack.pop()
                    if not isinstance(constraint_1, Constraint):
                        if constraint_1.isdigit():
                            constraint_1 = self.get_constraint(int(constraint_1))
                        else:
                            if constraint_1[0] == "~":
                                constraint_1 = Constraint([-self.literal_id_map[constraint_1[1:]]], [1], 0)
                            else:
                                constraint_1 = Constraint([self.literal_id_map[constraint_1]], [1], 0)
                    temp = constraint_1 - constraint_2
                elif statement[i] == '*':
                    constraint_2 = stack.pop()
                    constraint_2 = int(constraint_2)
                    constraint_1 = stack.pop()
                    if not isinstance(constraint_1, Constraint):
                        if constraint_1.isdigit():
                            constraint_1 = self.get_constraint(int(constraint_1))
                            antecedents.append(int(constraint_1))
                        else:
                            if constraint_1[0] == "~":
                                constraint_1 = Constraint([-self.literal_id_map[constraint_1[1:]]], [1], 0)
                            else:
                                constraint_1 = Constraint([self.literal_id_map[constraint_1]], [1], 0)
                    temp = constraint_1 * constraint_2
                elif statement[i] == 'd':
                    # print("DIVIDING CONSTRAINT")
                    constraint_2 = stack.pop()
                    constraint_2 = int(constraint_2)
                    constraint_1 = stack.pop()
                    if not isinstance(constraint_1, Constraint):
                        if constraint_1.isdigit():
                            constraint_1 = self.get_constraint(int(constraint_1))
                            antecedents.append(int(constraint_1))
                        else:
                            if constraint_1[0] == "~":
                                constraint_1 = Constraint([-self.literal_id_map[constraint_1[1:]]], [1], 0)
                            else:
                                constraint_1 = Constraint([self.literal_id_map[constraint_1]], [1], 0)
                    temp = constraint_1 / constraint_2
                    if self.loud:
                        print("dividing", constraint_1, constraint_2, temp)
                constr = copy.deepcopy(temp)
                stack.append(constr)
                temp = None
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
        # print("LINE: ", line[1:-1])
        constraint = self.constraint_parser(line[1:-1])
        # print("⭐", self.constraint_str(constraint), constraint)
        constraint.negation()
        # print("⭐", self.constraint_str(constraint), constraint)
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
        # if self.loud:
        #     print("⭐", self.constraint_str(rup_constraint),"⭐", rup_constraint)
        tau = rup_constraint.propagate([])
        # print(tau)
        tau = list(rup_constraint.literals)
        # print(tau)
        fired_constraints = []
        if self.loud:
            print("    ASSIGNMENT: ", tau)
        while True:
            for i in range(1, self.no_of_constraints+1):
                if i not in self.dead_constraints:
                    constraint = self.get_constraint(i)
                    if constraint.is_unsatisfied(tau):
                        fired_constraints.append(i)
                        # if self.loud:
                        #     print("    FIRED CONSTRAINTS: ", fired_constraints)
                        self.logger.warning(
                            str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                        self.constraints_known_to_propagate.update(fired_constraints)
                        return True
            if rup_constraint.is_unsatisfied(tau):
                self.logger.warning(str(self.no_of_constraints+1)+":"+" ".join([str(i) for i in fired_constraints]))
                return True
            unit_propagated = False
            for i in self.constraints_known_to_propagate:
                constraint = self.get_constraint(i)
                constraint_propagates = constraint.propagate(tau)
                if constraint_propagates != []:
                    fired_constraints.append(i)
                    tau += constraint_propagates
                    unit_propagated = True
                    # if self.loud:
                    #     print("    FIRED CONSTRAINT: ", i)
                    break
            if not unit_propagated:
                for i in range(1, self.no_of_constraints+1):
                    constraint = self.get_constraint(i)
                    constraint_propagates = constraint.propagate(tau)
                    if constraint_propagates != []:
                        fired_constraints.append(i)
                        tau += constraint_propagates
                        unit_propagated = True
                        # if self.loud:
                        #     print("    FIRED CONSTRAINT: ", i)
                        break
            if not unit_propagated:
                constraint_propagates = rup_constraint.propagate(tau)
                print("SELF PROPAGATES:", constraint_propagates)
                if constraint_propagates != []:
                    tau += constraint_propagates
                    unit_propagated = True
                    break
            if not unit_propagated:
                if self.loud:
                    print("    NOT RUP BUT PREVIOUSLY FIRED FIRED CONSTRAINTS: ", fired_constraints)
                return False

    def constraint_str(self, constraint:Constraint) -> str:
        """
        Returns the string representation of the constraint
        """
        id_literal_map = {v: k for k, v in self.literal_id_map.items()}
        constraint_string = ""
        # print(constraint.coefficients)
        for i in constraint.literals:
            if i < 0:
                constraint_string += " "+ str(constraint.coefficients[i]) + " ~" + str(id_literal_map[abs(i)])
            else:
                constraint_string += " "+ str(constraint.coefficients[i]) + " " + str(id_literal_map[abs(i)])
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
