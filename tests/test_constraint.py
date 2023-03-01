from ..constraint import Constraint


class TestConstraint:
    def test_create_constraint(self):
        literals = [1, -2, 3]
        coefficients = [1, 2, 3]
        degree = 5
        c = Constraint(literals, coefficients, degree)
        assert c.degree == degree
        assert c.literals == set(literals)
        assert c.coefficients == dict(zip(literals, coefficients))

    def test_create_constraint_with_empty_literals(self):
        literals = []
        coefficients = []
        degree = 5
        c = Constraint(literals, coefficients, degree)
        assert c.degree == degree
        assert c.literals == set(literals)
        assert c.coefficients == dict(zip(literals, coefficients))

    def test_create_constraint_with_empty_coefficients(self):
        literals = [1, -2, 3]
        coefficients = [0, 0, 0]
        degree = 5
        c = Constraint(literals, coefficients, degree)
        assert c.degree == degree
        assert c.literals == set([])
        assert c.coefficients == {}

    def test_constraint_add(self):
        c1 = Constraint([1, 2, 3], [1, 2, 3], 5)
        c2 = Constraint([1, -2, 3], [2, 4, 8], 5)
        c3 = Constraint([1, -2, 3], [3, 2, 11], 8)
        c4 = c1 + c2
        assert c4 == c3
        c4 = c2 + c1
        assert c4 == c3

    def test_constraint_subtraction(self):
        c1 = Constraint([1, 2, 3], [1, 2, 3], 5)
        c2 = Constraint([1, -2, 3], [2, 4, 8], 5)
        c3 = c1 + c2
        c4 = c3 - c2
        assert c4 == c1
        c4 = c3 - c1
        assert c4 == c2
        assert c4 * -1 == c1 - c3
    
    def test_constraint_division(self):
        c1 = Constraint([1, 2, 3], [1, 2, 3], 5)
        c2 = Constraint([1, 2, 3], [1, 1, 2], 3)
        assert c1 / 2 == c2
    