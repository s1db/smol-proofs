from typing import Tuple, Iterable
from collections import deque


class Constraint:
    def __init__(self, literals):
        self.literals_list = literals  # describes how exactly does this clause look like
        self.literals = set(literals)  # unordered unique set of literals
        self.size = len(self.literals)
    def partial_assignment(self, assignment: Iterable) -> list:
        """
        Performs partial assignment of this clause with give `assignment` and returns the resulting list of literals,
        i.e. if the clause is SAT then returns empty list, otherwise returns the remaining list of unassigned literals.
        :param assignment: the assignment
        :return: if the clause is SAT then returns empty list, otherwise returns the remaining list of unassigned
        literals
        """
        unassigned = set(self.literals)  # set has O(1) remove complexity
        for literal in assignment:
            if literal in self.literals:
                return []

            if -literal in self.literals:
                unassigned.remove(-literal)

        return list(unassigned)

    def is_satisfied(self, assignment: Iterable) -> bool:
        """
        :param: assignment: the assignment
        :return: True if the clause is satisfied in the `assignment`, i.e. one of its literals is True.
        """
        for literal in assignment:
            if literal in self.literals:
                return True
        return False

    def is_unsatisfied(self, assignment: Iterable) -> bool:
        """
        :param: assignment: the assignment
        :return: True if the clause is unsatisfied in the `assignment`, i.e. all of the literals are False.
        """
        false = 0
        for literal in assignment:
            if literal in self.literals:
                return False

            if -literal in self.literals:
                false += 1
        return false == self.size

    def is_unit(self, assignment: Iterable) -> bool:
        """
        :param: assignment: the assignment
        :return: True if the clause is unit in the `assignment`, i.e. only one literal is unassigned and the rest of
        them are False.
        """
        false = 0
        for literal in assignment:
            if literal in self.literals:
                return False

            if -literal in self.literals:
                false += 1

        return false == self.size - 1
    def unit(self, assignment: Iterable) -> int:
        """
        :param: assignment: the assignment
        :return: the unit literal if the clause is unit in the `assignment`, otherwise returns None.
        """
        false = 0
        for literal in assignment:
            if literal in self.literals:
                return None

            if -literal in self.literals:
                false += 1

        if false == self.size - 1:
            unit = iter(self.literals - set([-i for i in assignment]))
            return next(unit)
        return None


class PBModel:
    """
    The class which represents one formula in CNF.
    """
    def __init__(self, formula):
        self.formula = formula  # list of lists of clauses
        self.clauses = [Constraint(literals) for literals in self.formula]  # list of clauses
        self.unassigned = set()  # unordered unique set of unsigned variables in the formula (clauses use literals)
        self.adjacency_lists = {}  # dictionary with variables as keys and values as lists of clauses with this literal
        self.unit_clauses_queue = deque()  # queue for unit clauses
        self.assignment_stack = deque()  # stack for representing the current assignment for backtracking

        for clause in self.clauses:
            if clause.is_unit([]):
                self.unit_clauses_queue.append(clause)

            # For every literal in clause (*)
            for literal in clause.literals:
                variable = abs(literal)
                self.unassigned.add(variable)

                # (*) find out if it already has list of clauses (key) in adjacency_lists. If it does, then update that
                # list with this clause. If it does not, then create new element of dictionary `adjacency_lists` with
                # key being this variable and then create its value as a list with this clause.
                if variable in self.adjacency_lists:
                    if clause not in self.adjacency_lists[variable]:
                        self.adjacency_lists[variable].append(clause)

                else:
                    self.adjacency_lists[variable] = [clause]

    def is_satisfied(self) -> bool:
        """
        :return: True if the formula is satisfied, i.e. if all the clauses are satisfied
        """
        for clause in self.clauses:
            if not clause.is_satisfied(self.assignment_stack):
                return False

        return True

    def partial_assignment(self, assignment: Iterable) -> bool:
        """
        Perform the partial assignment of literals from `assignment` by setting them to True and opposite literals to
        False.
        :param assignment: list of literals to be set to True
        :return: True if the assignment was successful, False otherwise, i.e. one or more clauses are unsatisfied by
                 this assignment.
        """
        for literal in assignment:
            # Remove corresponding variable from the unassigned set of the formula and add literal to assignment stack
            self.unassigned.remove(abs(literal))
            self.assignment_stack.append(literal)

            # For every clause in the adjacency list of this variable find out which
            # clauses become unit and which become unsatisfied in the current assignment
            for clause in self.adjacency_lists[abs(literal)]:
                if clause.is_unsatisfied(self.assignment_stack):
                    return False

                if clause.is_unit(self.assignment_stack):
                    self.unit_clauses_queue.append(clause)

        return True

    def undo_partial_assignment(self, decision_literal: int) -> None:
        """
        Undo partial assignment of this formula by removing literals from `self.assignment` up until the
        `decision_literal`.
        :param decision_literal: the last literal which assignment is undone
        """
        self.unit_clauses_queue.clear()
        while self.assignment_stack:
            literal = self.assignment_stack.pop()
            self.unassigned.add(abs(literal))
            if literal == decision_literal:
                break

    def unit_propagation(self) -> Tuple[list, bool]:
        """
        Performs a unit propagation of this formula.
        :return: a tuple (assignment, success) with assignment containing literals derived by unit propagation and
                success representing whether the unit propagation was successful, i.e. no clause is unsatisfied by the
                derived assignment, or False, if at least one clause is unsatisfied.
        """
        propagated_literals = []
        while self.unit_clauses_queue:
            unit_clause = self.unit_clauses_queue.popleft()
            # get the resulting literal from the unit clause given by the current assignment
            literal = unit_clause.partial_assignment(self.assignment_stack)
            propagated_literals += literal
            if not self.partial_assignment(literal):
                return propagated_literals, False

        return propagated_literals, True

    def get_decision_literal(self) -> int:
        """
        Finds the unassigned literal which occurs in the largest number of not satisfied clauses.
        :return: the decision literal
        """
        number_of_clauses = 0
        decision_literal = None
        for variable in self.unassigned:
            positive_clauses = 0
            negative_clauses = 0
            for clause in self.adjacency_lists[variable]:
                if not clause.is_satisfied(self.assignment_stack):
                    unassigned = clause.partial_assignment(self.assignment_stack)
                    if variable in unassigned:
                        positive_clauses += 1

                    if -variable in unassigned:
                        negative_clauses += 1

            if positive_clauses > number_of_clauses and positive_clauses > negative_clauses:
                number_of_clauses = positive_clauses
                decision_literal = variable

            if negative_clauses > number_of_clauses:
                number_of_clauses = negative_clauses
                decision_literal = -variable

        return decision_literal

    def print(self) -> None:
        """
        Prints basic information about the formula.
        """
        # Not used in the dpll program itself.
        print("Formula: ")
        print(self.formula)
        print("Clauses: ")
        for clause in self.clauses:
            print(clause.literals)
        print("Literals: ")
        # print(self.literals)
        print("Variables: ")
        # print(self.variables)
        print("Unassigned variables: ")
        print(self.unassigned)
        print("Adjacency lists: ")
        for variable, adj_list in self.adjacency_lists.items():
            print(variable, ": ")
            for clause in adj_list:
                print(clause.literals)


if __name__ == "__main__":
    model = PBModel([[8, 9, 2, 3],[8, 9, -2, 3], [8, 9, 4, -3], [8, 9, -4, -3]])
    model.print()