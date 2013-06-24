from pest.worm import Worm


class Grapefruit(object):
    def __init__(self):
        pass

    def fall(self):
        my_worm = Worm()
        is_good_day = my_worm.crawl()

        if is_good_day:
            print "Grapefruits fall like any other fruit."
        else:
            print "Wormy grapefruits are yucky!"

        return is_good_day
