import json
import os
from nose.tools import eq_
from daf_fruit_dist.build.constants import \
    PYTHON_SDIST, \
    PYTHON_EGG, \
    PYTHON_FREEZE
from daf_fruit_dist.build.id import Id
from daf_fruit_dist.build.module import Module


def assert_artifacts(module):
    artifacts = module.artifacts

    eq_(len(artifacts), 3)
    eq_(artifacts[0].type, PYTHON_EGG)
    eq_(artifacts[0].sha1, "EggSHA1SHA1SHA1")
    eq_(artifacts[0].md5, "EggMD5MD5MD5")
    eq_(artifacts[0].name, "pointy-stick-5.2.egg")
    eq_(artifacts[1].type, PYTHON_FREEZE)
    eq_(artifacts[1].sha1, "FreezeSHA1SHA1SHA1")
    eq_(artifacts[1].md5, "FreezeMD5MD5MD5")
    eq_(artifacts[1].name, "pointy-stick-5.2.txt")
    eq_(artifacts[2].type, PYTHON_SDIST)
    eq_(artifacts[2].sha1, "c846dc274ccbefd9736b9e48011d2e3a1d149e72")
    eq_(artifacts[2].md5, "e85249246810d56aad3f198deea74bbb")
    eq_(artifacts[2].name, "pointy-stick-5.2.txt")


def create_module_builder(
        artifacts=None,
        dependencies=None,
        treat_none_as_empty=True):

    module_builder = Module.Builder(
        id=Id(
            group_id="defend.against.fruit",
            artifact_id="pointy-stick",
            version="5.2"),
        properties={'banana': 'monkey love', 'orange': 'gorilla color'},
        artifacts=artifacts,
        dependencies=dependencies,
        treat_none_as_empty=treat_none_as_empty
    )
    return module_builder


def add_some_dependencies(module_builder):
    module_builder.add_dependency(
        type=PYTHON_SDIST,
        sha1="GunSHA1SHA1SHA1",
        md5="GunMD5MD5MD5",
        id=Id(
            group_id="defend.against.fruit",
            artifact_id="gun",
            version="2.3"))

    module_builder.add_dependency(
        type=PYTHON_SDIST,
        md5="WeightMD5MD5MD5",
        id=Id(
            group_id="defend.against.fruit",
            artifact_id="weight",
            version="5.6.7"))


def assert_dependencies(module):
    dependencies = module.dependencies

    eq_(dependencies[0].type, PYTHON_SDIST)
    eq_(dependencies[0].sha1, "GunSHA1SHA1SHA1")
    eq_(dependencies[0].md5, "GunMD5MD5MD5")
    eq_(dependencies[0].id.group_id, "defend.against.fruit")
    eq_(dependencies[0].id.artifact_id, "gun")
    eq_(dependencies[0].id.version, "2.3")

    eq_(dependencies[1].type, PYTHON_SDIST)
    eq_(dependencies[1].sha1, None)
    eq_(dependencies[1].md5, "WeightMD5MD5MD5")
    eq_(dependencies[1].id.group_id, "defend.against.fruit")
    eq_(dependencies[1].id.artifact_id, "weight")
    eq_(dependencies[1].id.version, "5.6.7")


def add_some_artifacts(module_builder):
    module_builder.add_artifact(
        type=PYTHON_EGG,
        sha1="EggSHA1SHA1SHA1",
        md5="EggMD5MD5MD5",
        name="pointy-stick-5.2.egg")
    module_builder.add_artifact(
        type=PYTHON_FREEZE,
        sha1="FreezeSHA1SHA1SHA1",
        md5="FreezeMD5MD5MD5",
        name="pointy-stick-5.2.txt")
    dir_name = os.path.dirname(__file__)
    fake_artifact_file = os.path.join(dir_name, 'pointy-stick-5.2.txt')
    module_builder.add_file_as_artifact(
        type=PYTHON_SDIST,
        file=fake_artifact_file)


def assert_module_basics(module):
    eq_(module.id.group_id, "defend.against.fruit")
    eq_(module.id.artifact_id, "pointy-stick")
    eq_(module.id.version, "5.2")
    eq_(module.properties['banana'], 'monkey love')
    eq_(module.properties['orange'], 'gorilla color')


def round_trip_to_and_from_wire_format(
        domain_object,
        from_json_data_func,
        domain_object_assertion_func=None):

    # Perform assertions if any on the domain object before starting
    if domain_object_assertion_func:
        domain_object_assertion_func(domain_object)

    # Take the domain object down to wire-level format
    json_data_1 = domain_object.as_json_data
    domain_object_as_json_1 = json.dumps(json_data_1, sort_keys=True, indent=4)
    assert domain_object_as_json_1, "json string is non-null"

    # Read the wire-level data back into a domain object
    json_data_2 = json.loads(domain_object_as_json_1)
    domain_object_2 = from_json_data_func(json_data_2)

    # See if the re-hydrated domain object still passes the assertions
    # (if any)
    if domain_object_assertion_func:
        domain_object_assertion_func(domain_object_2)

    # Take the re-hydrated domain object back down to the wire-level
    # format again
    json_data_3 = domain_object_2.as_json_data
    domain_object_as_json_3 = json.dumps(json_data_3, sort_keys=True, indent=4)
    assert domain_object_as_json_3, "json string is non-null"

    # Assert the wire-level format looked identical both times
    eq_(domain_object_as_json_1, domain_object_as_json_3)
