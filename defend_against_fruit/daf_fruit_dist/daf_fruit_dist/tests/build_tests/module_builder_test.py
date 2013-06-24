import json
from nose.tools import eq_
from daf_fruit_dist.build.constants import PYTHON_SDIST
from daf_fruit_dist.build.module import Module
from daf_fruit_dist.tests.build_tests import module_test_helper


def typical_artifacts_no_dependencies_test():
    module_builder = module_test_helper.create_module_builder()

    module_test_helper.add_some_artifacts(module_builder)

    module = module_builder.build()

    module_test_helper.assert_module_basics(module)

    module_test_helper.assert_artifacts(module)


def typical_artifacts_and_dependencies_test():
    module_builder = module_test_helper.create_module_builder()

    module_test_helper.add_some_artifacts(module_builder)

    module_test_helper.add_some_dependencies(module_builder)

    module = module_builder.build()

    module_test_helper.assert_module_basics(module)

    module_test_helper.assert_artifacts(module)

    module_test_helper.assert_dependencies(module)

    json_data = module.as_json_data
    json_string = json.dumps(json_data, sort_keys=True, indent=4)

    assert json_string, "json string is non-null"


def _create_complete_module():
    module_builder = module_test_helper.create_module_builder()
    module_test_helper.add_some_artifacts(module_builder)
    module_test_helper.add_some_dependencies(module_builder)
    module = module_builder.build()
    return module


def json_encoding_decoding_test():
    module = _create_complete_module()

    module_test_helper.round_trip_to_and_from_wire_format(
        module,
        Module.from_json_data,
        module_test_helper.assert_module_basics)


def null_vs_empty_dependencies_test():
    """Missing artifacts or dependencies should be None not an empty collection."""
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module = module_builder.build()

    eq_(module.artifacts, None, "artifacts start as None")
    eq_(module.dependencies, None, "dependencies start as None")

    #Take the domain object down to wire-level format
    json_string = json.dumps(module.as_json_data, sort_keys=True, indent=4)

    #Read the wire-level data back into a domain object
    json_data_2 = json.loads(json_string)
    re_hydrated_module = Module.from_json_data(json_data_2)

    eq_(re_hydrated_module.artifacts, None, "artifacts of None survives round-trip on the wire")
    eq_(re_hydrated_module.dependencies, None, "artifacts of None survives round-trip on the wire")


def ensure_artifacts_defined_test():
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module_builder.ensure_artifacts_defined()
    module = module_builder.build()

    eq_(module.artifacts, (), "artifacts defined but empty")
    eq_(module.dependencies, None, "dependencies not defined")


def ensure_dependencies_defined_test():
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module_builder.ensure_dependencies_defined()
    module = module_builder.build()

    eq_(module.artifacts, None, "artifacts not defined")
    eq_(module.dependencies, (), "dependencies defined but empty")


def treat_none_as_empty_false__empty_artifacts__undefined_dependencies_test():
    module_builder = module_test_helper.create_module_builder(
        artifacts=[],
        dependencies=None,
        treat_none_as_empty=False)
    module = module_builder.build()

    eq_(module.artifacts, (), "artifacts defined but empty")
    eq_(module.dependencies, None, "dependencies not defined")


def treat_none_as_empty_false__undefined_artifacts__empty_dependencies_test():
    module_builder = module_test_helper.create_module_builder(
        artifacts=None,
        dependencies=[],
        treat_none_as_empty=False)
    module = module_builder.build()

    eq_(module.artifacts, None, "artifacts not defined")
    eq_(module.dependencies, (), "dependencies defined but empty")


def ensure_artifacts_defined_non_empty_collection_test():
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module_test_helper.add_some_artifacts(module_builder)
    module_builder.ensure_artifacts_defined()
    module = module_builder.build()

    module_test_helper.assert_artifacts(module)
    eq_(module.dependencies, None, "dependencies not defined")


def ensure_dependencies_defined__non_empty_collection_test():
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module_test_helper.add_some_dependencies(module_builder)

    module_builder.ensure_dependencies_defined()
    module = module_builder.build()

    eq_(module.artifacts, None, "artifacts not defined")
    module_test_helper.assert_dependencies(module)


def module_builder_from_module_test():
    moduleA = _create_complete_module()

    module_builderB = Module.Builder.from_another_module(moduleA)
    moduleB = module_builderB.build()

    eq_(moduleB, moduleA)

    #Add some more artifacts. Will blow up if the internal collection isn't mutable as it should be.
    module_test_helper.add_some_artifacts(module_builderB)
    module_test_helper.add_some_dependencies(module_builderB)


def module_builder_from_module_with_dependencies_of_none_test():
    #Intentionally exclude dependencies while ensuring None is treated as None.
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module_test_helper.add_some_artifacts(module_builder)
    moduleA = module_builder.build()

    module_builderB = Module.Builder.from_another_module(moduleA, treat_none_as_empty=False)
    moduleB = module_builderB.build()

    eq_(moduleB, moduleA)


def module_builder_from_module_copy_dependencies_false_test():
    module_builder = module_test_helper.create_module_builder(treat_none_as_empty=False)
    module_test_helper.add_some_artifacts(module_builder)
    module_test_helper.add_some_dependencies(module_builder)
    moduleA = module_builder.build()

    module_builderB = Module.Builder.from_another_module(moduleA, treat_none_as_empty=False, copy_dependencies=False)
    moduleB = module_builderB.build()

    eq_(moduleB.id, moduleA.id)
    eq_(moduleB.properties, moduleA.properties)
    eq_(moduleB.artifacts, moduleA.artifacts)
    eq_(moduleB.dependencies, None)

    module_builderC = Module.Builder.from_another_module(moduleA, treat_none_as_empty=True, copy_dependencies=False)
    moduleC = module_builderC.build()

    eq_(moduleC.id, moduleA.id)
    eq_(moduleC.artifacts, moduleA.artifacts)
    eq_(moduleC.properties, moduleA.properties)
    eq_(moduleC.dependencies, ())


def dependency_missing_id_test():
    module_builder = module_test_helper.create_module_builder()

    module_test_helper.add_some_artifacts(module_builder)

    #No id specified
    module_builder.add_dependency(
        type=PYTHON_SDIST,
        id=None,
        sha1="GunSHA1SHA1SHA1",
        md5="GunMD5MD5MD5"
    )

    module = module_builder.build()

    module_test_helper.round_trip_to_and_from_wire_format(
        module,
        Module.from_json_data,
        module_test_helper.assert_module_basics)
