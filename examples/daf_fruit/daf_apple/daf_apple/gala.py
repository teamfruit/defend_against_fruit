from daf_pest.worm import Worm


class Gala(object):
    def __init__(self):
        pass

    def fall(self):
        my_worm = Worm()
        is_good_day = my_worm.crawl()

        if is_good_day:
            print "Sum of the forces equals the change in momentum of the system"
        else:
            print "Any worm in my apple should at least be a happy worm. Time for beer!"

        return is_good_day
