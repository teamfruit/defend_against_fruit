from daf_apple.gala import Gala
from daf_citrus.pomelo import Pomelo


class WickerBasket(object):
    def __init__(self):
        pass

    def feed_dwarfs(self):
        my_fruit = Pomelo()
        is_good_day = my_fruit.fall()

        if is_good_day:
            print("Hi Ho Hi Ho its off to work we go.")
        else:
            print("That wicked witch put worms in our Pomelos.")

        return is_good_day

    def feed_snow_white(self):
        my_apple = Gala()
        is_good_day = my_apple.fall()

        if is_good_day:
            print("Prince charming is here. Even grumpy is happy!")
        else:
            print("I'm falling asleep. Darn that wicked witch!")

        return is_good_day
