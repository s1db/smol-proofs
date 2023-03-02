"""
Pseudo Boolean Constraint Class
Implements most PB constraint operations.
"""

from typing import Iterable
from collections import defaultdict
import copy
from math import ceil


class Constraint:
    """
    Pseudo Boolean Constraint Class 
    """
    def __init__(self, literals, coefficients, degree):
        self.literals = set(literals)
        self.coefficients = defaultdict(int)
        self.degree = degree  # of falsity
        self.no_of_literals = len(self.literals)
        for literal, coefficient in zip(literals, coefficients):
            self.coefficients[literal] += coefficient
        if self.no_of_literals != len(self.coefficients):
            raise ValueError("unequal number of literals and coefficients.")
        self.coefficient_normalized_form()

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
        Deletes the literal and/or the negative
        of the literal from the constraint.
        """
        literals = self.literals
        if literal in literals:
            self.literals.remove(literal)
            del self.coefficients[literal]
        if -literal in literals:
            self.literals.remove(-literal)
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
        :return: the literals that need be added
            to the assignment to satisfy the constraint.
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

    # def implies(self, constraint) -> int:
    #     """
    #     TODO: check if self semantically implies other constraint
    #     :param: constraint
    #     :return: True if self semantically implies other constraint
    #     """
    #     weaken_cost = 0
    #     for i in constraint.literals:
    #         if i not in self.literals:
    #             return False
    #         else:
    #             if self.coefficients[i] < constraint.coefficients[i]:
    #                 return False
    #             else:
    #                 weaken_cost += self.coefficients[i] - \
    #                     constraint.coefficients[i]
    #     if self.degree < constraint.degree:
    #         return False
    #     else:
    #         weaken_cost += self.degree - constraint.degree
    #     return weaken_cost

    # def saturation(self):
    #     for i in self.literals:
    #         self.coefficients[i] = min(self.coefficients[i], self.degree)

    def __add__(self, other: 'Constraint'):
        self.literal_normalized_form()
        other.literal_normalized_form()
        degree = self.degree + other.degree
        literals = set(self.literals) | set(other.literals)
        literal_coefficient_pair = {i: self.coefficients.get(
            i, 0) + other.coefficients.get(i, 0) for i in literals}
        [*literals], [*coefficients] = zip(*literal_coefficient_pair.items())
        self.coefficient_normalized_form()
        other.coefficient_normalized_form()
        new_constraint = Constraint(literals, coefficients, degree)
        new_constraint.coefficient_normalized_form()
        return new_constraint

    def __mul__(self, other: int):
        new_constraint = copy.deepcopy(self)
        for i in new_constraint.literals:
            new_constraint.coefficients[i] *= other
        new_constraint.degree *= other
        new_constraint.coefficient_normalized_form()
        return new_constraint

    def __sub__(self, other: 'Constraint'):
        diff = copy.deepcopy(other)
        diff = diff * -1
        diff = self + diff
        diff.coefficient_normalized_form()
        return diff

    def __truediv__(self, other: int):
        div = copy.deepcopy(self)
        for i in div.literals:
            div.coefficients[i] = ceil(div.coefficients[i] / other)
        div.degree = ceil(div.degree / other)
        div.coefficient_normalized_form()
        return div

    def __eq__(self, other: 'Constraint') -> bool:
        """
        :param: other: the other constraint
        """
        self.coefficient_normalized_form()
        other.coefficient_normalized_form()
        if self.degree != other.degree:
            return False
        if sorted(self.literals) != sorted(other.literals):
            return False
        for i in self.literals:
            if self.coefficients[i] != other.coefficients[i]:
                return False
        return True

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

    def __repr__(self) -> str:
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
