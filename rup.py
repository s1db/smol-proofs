from collections import deque
from typing import List, Iterable, Set, Dict, Tuple, Union
from constraint import Constraint
# walks like sat rup, 
# talks like sat rup, 
# but one day i'll turn it into pb rup

class RUPchecker:
    def __init__(self, F:List[Constraint], Q):
        self.F = [Constraint(clause) for clause in F] # formula
        # store Q as a queue
        self.Q = deque([Constraint(clause) for clause in Q][::-1])

    def RUPchecker(self) -> str:
        if not self.Q:
            return "invalid refutation"
        while self.Q:
            L = self.Q.pop()
            print("checking", L.literals_list)
            if not self.RUP(self.F, L):
                return "validation failed"
            self.F.append(L)
            print("added", L.literals_list)
        return "refutation validated"

    def RUP(self, F:List[Constraint], L) -> bool:
        tau = [-i for i in L.literals_list]
        while True:
            unit_propagated = False
            for c in F:
                evaluated = c.is_unsatisfied(tau)
                if evaluated:
                    return True
            for c in F:
                c_is_unit = c.unit(tau)
                if c_is_unit != None:
                    tau.append(c_is_unit)
                    unit_propagated = True
                    break
            if not unit_propagated:
                return False

if __name__ == "__main__":
    formula = [[8, 9, 2, 3],[8, 9, -2, 3], [8, 9, 4, -3], [8, 9, -4, -3]]
    proof = [[8, 9, -3],[8, 9,  3],[8, 9]]
    check = RUPchecker(formula, proof)
    print(check.RUPchecker())