import os


class Worm(object):
    def __init__(self):
        pass

    def crawl(self):
        be_happy_string = os.environ.get('BE_HAPPY', "true")
        is_good_day = be_happy_string.lower().strip() == "true"

        if is_good_day:
            print "I love to crawl"
        else:
            print "I don't want to crawl today"

        return is_good_day
