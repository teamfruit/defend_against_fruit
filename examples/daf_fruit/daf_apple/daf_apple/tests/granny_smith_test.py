from daf_apple.granny_smith import GrannySmith


def fall_test():
    my_fruit = GrannySmith()
    did_it_fall = my_fruit.fall()
    assert did_it_fall, "Granny says it is a good day for Newtonian physics"
