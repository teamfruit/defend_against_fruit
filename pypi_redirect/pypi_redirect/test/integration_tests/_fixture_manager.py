_active_fixture = None


def activate_fixture(fixture_factory_fn):
    fixture = fixture_factory_fn()
    _activate_fixture(fixture)


def _activate_fixture(fixture):
    global _active_fixture

    if _active_fixture:
        _active_fixture.teardown()

    _active_fixture = fixture

    if _active_fixture:
        _active_fixture.setup()


def teardown():
    _activate_fixture(None)
