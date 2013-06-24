from daf_pest.worm import Worm


class Pomelo(object):
    def __init__(self):
        pass

    def fall(self):
        my_worm = Worm()
        is_good_day = my_worm.crawl()

        if is_good_day:
            print "Messy juicy goodness in a vacuum falls the same as an apple in a vacuum"
        else:
            print "Worms in a Pomelo are nasty"

        return is_good_day
