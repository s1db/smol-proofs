from find_antecedent import PBConstraint

def test_pb_constraint():
    a = PBConstraint([1, 2, 3], [1, 2, 3], 3)
    b = PBConstraint([1, -2, 3], [1, 3, -2], 4)
    print("not normalized",b)
    b.literal_normalized_form()
    print("literal normalized",b)
    b.coefficient_normalized_form()
    print("coefficient normalized",b)


# def test_addition():
#     a = PBConstraint([1, 2, 3], [1, 2, 3], 3)
#     b = PBConstraint([1, -2, 3], [1, 3, 2], 4)
#     c = a + b
#     assert c == PBConstraint([1, 2, 3, 1, -2, 3], [1, 2, 3, 1, 3, 2], 7)

if __name__ == "__main__":
    test_pb_constraint()