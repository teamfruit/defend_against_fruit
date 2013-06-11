import _fixture_manager


class FixtureBaz(object):
    def setup(self):
        print 'FixtureBaz.setup'

    def teardown(self):
        print 'FixtureBaz.teardown'


def setup_module():
    _fixture_manager.activate_fixture(FixtureBaz)


def teardown_module():
    _fixture_manager.teardown()


def baz1_test():
    print '    baz1_test'


def baz2_test():
    print '    baz2_test'


def baz3_test():
    print '    baz3_test'
