from daf_pest.worm import Worm

def crawl_test():
    my_worm = Worm()
    did_it_crawl = my_worm.crawl()
    assert did_it_crawl, "Worm thinks it is a good day for crawling"
