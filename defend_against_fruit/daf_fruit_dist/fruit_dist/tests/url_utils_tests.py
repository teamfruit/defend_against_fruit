from nose.tools import eq_, raises
from fruit_dist.url_utils import subtract_index_url


def validate_subtract_index_url(index_url, pkg_url, expected_tail):
    pip_tail = subtract_index_url(index_url=index_url, pkg_url=pkg_url)
    eq_(pip_tail, expected_tail)


@raises(RuntimeError)
def validate_subtract_index_url_failure(index_url, pkg_url):
    subtract_index_url(index_url=index_url, pkg_url=pkg_url)


def test_subtract_index_url_happy_path():
    index_url_pkg_url_pip_tail_tuples = (
        ('http://artifactory.defendagainstfruit.com:801/artifactory/team-fruit/python',
         'http://artifactory.defendagainstfruit.com:801/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz',
         'nose/nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com:801/artifactory/team-fruit/python/',
         'http://artifactory.defendagainstfruit.com:801/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz',
         'nose/nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz',
         'nose/nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz',
         'nose/nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/nose-1.2.1.tar.gz',
         'nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/nose-1.2.1.tar.gz',
         'nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com/team-fruit/python',
         'http://artifactory.defendagainstfruit.com/team-fruit/python/nose/nose-1.2.1.tar.gz',
         'nose/nose-1.2.1.tar.gz'),

        ('https://artifactory.defendagainstfruit.com:801/artifactory/team-fruit/python',
         'https://artifactory.defendagainstfruit.com:801/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz',
         'nose/nose-1.2.1.tar.gz')
    )
    for index_url, pkg_url, expected_tail in index_url_pkg_url_pip_tail_tuples:
        yield validate_subtract_index_url, index_url, pkg_url, expected_tail


def test_subtract_index_url_unhappy_path():
    index_url_pkg_url_tuples = (
        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/ugly',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python'),

        ('http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/'),

        ('artifactory.defendagainstfruit.com/artifactory/team-fruit/python',
         'http://artifactory.defendagainstfruit.com/artifactory/team-fruit/python/nose/nose-1.2.1.tar.gz'),

        ('ladies and gentlemen',
         'hobos and tramps')
    )
    for index_url, pkg_url in index_url_pkg_url_tuples:
        yield validate_subtract_index_url_failure, index_url, pkg_url
