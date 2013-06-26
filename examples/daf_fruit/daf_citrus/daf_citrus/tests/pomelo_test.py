from daf_citrus.pomelo import Pomelo


def fall_test():
    my_fruit = Pomelo()
    did_it_fall = my_fruit.fall()
    assert did_it_fall, "Juicy Pomelos make it a good day for " \
                        "Newtonian physics"
