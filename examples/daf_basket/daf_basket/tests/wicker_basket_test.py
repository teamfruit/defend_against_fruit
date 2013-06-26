from daf_basket.wicker_basket import WickerBasket


def feed_snow_white_test():
    my_basket = WickerBasket()
    did_she_dance_at_the_ball = my_basket.feed_snow_white()
    assert did_she_dance_at_the_ball, \
        "Snow White didn't dance in the ball"


def feed_dwarfs_test():
    my_basket = WickerBasket()
    did_the_dwarfs_sing_in_the_hall = my_basket.feed_dwarfs()
    assert did_the_dwarfs_sing_in_the_hall, \
        "The dwarfs didn't sing in the hall"
