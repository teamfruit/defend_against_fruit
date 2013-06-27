from nose.tools import eq_

from daf_fruit_dist.build.agent import Agent
from daf_fruit_dist.build.build_info import BuildInfo
from daf_fruit_dist.build.build_retention import BuildRetention
from daf_fruit_dist.build.constants import PYTHON_SDIST
from daf_fruit_dist.build.id import Id
from daf_fruit_dist.build.module import Module
from daf_fruit_dist.tests.build_tests import module_test_helper


def _create_build_info_builder():
    bi_builder = BuildInfo.Builder(
        version="2.2.2",
        name="lets-build",
        number="123456789",
        type=PYTHON_SDIST,
        started="100",
        duration_millis=10000,
        artifactory_principal="dude",
        agent=Agent(name="defend_against_fruit", version="5.2"),
        build_agent=Agent(name="TeamCity", version="1.3"),
        build_retention=BuildRetention(
            count=5,
            delete_build_artifacts=False,
            build_numbers_not_to_be_discarded=[111, 999])
    )
    return bi_builder


def _create_build_info():
    bi_builder = _create_build_info_builder()

    moduleA = _create_module()
    bi_builder.add_module(moduleA)

    moduleB = _create_module()
    bi_builder.add_module(moduleB)

    moduleC = _create_module()
    bi_builder.add_module(moduleC)

    build_info = bi_builder.build()

    return build_info


def _assert_basic_attributes(build_info):
    eq_(build_info.name, "lets-build")
    eq_(build_info.version, "2.2.2")
    eq_(build_info.name, "lets-build")
    eq_(build_info.number, "123456789")
    eq_(build_info.type, PYTHON_SDIST)
    eq_(build_info.started, "100")
    eq_(build_info.duration_millis, 10000)
    eq_(build_info.artifactory_principal, "dude")
    eq_(build_info.agent.name, "defend_against_fruit")
    eq_(build_info.agent.version, "5.2")
    eq_(build_info.build_agent.name, "TeamCity")
    eq_(build_info.build_agent.version, "1.3")
    eq_(build_info.build_retention.count, 5)
    eq_(build_info.build_retention.delete_build_artifacts, False)
    eq_(build_info.build_retention.build_numbers_not_to_be_discarded,
        [111, 999])


def _create_module():
    module_builder = module_test_helper.create_module_builder()

    module_test_helper.add_some_artifacts(module_builder)

    module_test_helper.add_some_dependencies(module_builder)

    module = module_builder.build()

    return module


def typical_usage_test():
    build_info = _create_build_info()

    _assert_basic_attributes(build_info)


def equals_and_hash_expected_equality_test():
    """
    Test equals and hashcode behavior of BuildInfo and the containing
    classes.

    If I have messed up I'm pretty sure it will show up as a false
    negative not a false positive. The most likely problem is that I
    have tried to hash some structure that will throw an unhashable
    type error.
    """
    build_info_A = _create_build_info()
    build_info_B = _create_build_info()
    eq_(build_info_A, build_info_B)

    eq_(build_info_A.__hash__(), build_info_B.__hash__())


def equals_and_hash_expected_difference_test():
    """
    quick check to make sure I am not causing problems by feeding a dict
    to frozenset.
    """
    bi_builder_C = _create_build_info_builder()
    module_builder_C = Module.Builder(
        id=Id(
            group_id="defend.against.fruit",
            artifact_id="pointy-stick",
            version="5.2"),
        properties={'ape', 'lets swing'})
    bi_builder_C.add_module(module_builder_C.build())
    build_info_C = bi_builder_C.build()

    bi_builder_D = _create_build_info_builder()
    module_builder_D = Module.Builder(
        id=Id(
            group_id="defend.against.fruit",
            artifact_id="pointy-stick",
            version="5.2"),
        properties={'ape', 'lets make funny faces'})
    bi_builder_D.add_module(module_builder_D.build())
    build_info_D = bi_builder_D.build()

    assert build_info_C != build_info_D, \
        "different property values should result in unequal BuildInfo " \
        "instances"

    assert build_info_C.__hash__() != build_info_D.__hash__(), \
        "different property values should result in unequal hash values"


def json_encoding_decoding_test():
    build_info = _create_build_info()

    module_test_helper.round_trip_to_and_from_wire_format(
        build_info,
        BuildInfo.from_json_data,
        _assert_basic_attributes)


def no_modules_test():
    bi_builder = _create_build_info_builder()
    build_info = bi_builder.build()

    module_test_helper.round_trip_to_and_from_wire_format(
        build_info,
        BuildInfo.from_json_data,
        _assert_basic_attributes)


def single_module_without_artifacts_test():
    bi_builder = _create_build_info_builder()
    module_builderA = module_test_helper.create_module_builder()
    module_test_helper.add_some_dependencies(module_builderA)
    moduleA = module_builderA.build()

    bi_builder.add_module(moduleA)
    build_info = bi_builder.build()

    module_test_helper.round_trip_to_and_from_wire_format(
        build_info,
        BuildInfo.from_json_data,
        _assert_basic_attributes)


def single_module_without_dependencies_test():
    bi_builder = _create_build_info_builder()
    module_builderA = module_test_helper.create_module_builder()
    module_test_helper.add_some_artifacts(module_builderA)
    moduleA = module_builderA.build()

    bi_builder.add_module(moduleA)
    build_info = bi_builder.build()

    module_test_helper.round_trip_to_and_from_wire_format(
        build_info,
        BuildInfo.from_json_data,
        _assert_basic_attributes)


def single_module_with_missing_module_attributes_test():
    module_builder = Module.Builder(
        id=None,
        #id=Id(
        #   group_id="defend.against.fruit",
        #   artifact_id="pointy-stick",
        #   version="5.2"),
        properties={'banana': 'monkey love',
                    'orange': 'gorilla color'})

    module_test_helper.add_some_artifacts(module_builder)

    module_test_helper.add_some_dependencies(module_builder)

    module = module_builder.build()

    bi_builder = _create_build_info_builder()
    bi_builder.add_module(module)

    build_info = bi_builder.build()

    module_test_helper.round_trip_to_and_from_wire_format(
        build_info,
        BuildInfo.from_json_data,
        _assert_basic_attributes)


def missing_basic_attributes_test():
    bi_builder = BuildInfo.Builder(
        version="2.2.2",
        name="lets-build",
        #number="123456789",
        type=PYTHON_SDIST,
        #started="100",
        duration_millis=10000,
        artifactory_principal="dude",
        #agent=Agent(name="defend_against_fruit", version="5.2"),
        #build_agent=Agent(name="TeamCity", version="1.3"),
        build_retention=BuildRetention(
            count=5,
            delete_build_artifacts=False)
    )

    bi_builder.add_module(_create_module())
    build_info = bi_builder.build()

    module_test_helper.round_trip_to_and_from_wire_format(
        build_info,
        from_json_data_func=BuildInfo.from_json_data)
