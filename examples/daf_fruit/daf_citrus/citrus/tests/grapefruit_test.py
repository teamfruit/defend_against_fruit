from citrus.grapefruit import Grapefruit


def fall_test():
    my_fruit = Grapefruit()
    did_it_fall = my_fruit.fall()
    assert did_it_fall, "Good day for Grapefruit inspired Newtonian physics"
