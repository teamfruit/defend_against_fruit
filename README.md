Defend Against Fruit
====================

Please [see the wiki](https://github.com/teamfruit/defend_against_fruit/wiki) for project details.


Usage Hints
-----------
To run ci:

    > ci

To run ci with publishing:

    > set BUILD_NAME=foobar
    > set MAJOR_VERSION=1
    > set MINOR_VERSION=1
    > set BUILD_NUMBER=0
    > ci --publish

Artifactory considerations
--------------------------
Pip and distribute are installed into the virtual environment using virtualenv.
When creating a build-info the CI tooling will leverage the Artifactory REST API
to determine checksums for every dependency found by pip freeze. For this to work
the same version of distribute used by virtualenv must be found in Artifactory.
At present this is distribute-0.6.34.tar.gz


"A table, a chair, a bowl of fruit, and a violin; what else does a man need to be happy?"
--Albert Einstein

