from daf_apple.gala import Gala


def fall_test():
    my_fruit = Gala()
    did_it_fall = my_fruit.fall()
    assert did_it_fall, "Good day for Newtonian physics"
