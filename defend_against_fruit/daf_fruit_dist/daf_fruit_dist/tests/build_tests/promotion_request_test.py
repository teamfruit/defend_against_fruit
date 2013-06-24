from nose.tools import eq_
from daf_fruit_dist.build.promotion_request import PromotionRequest
from daf_fruit_dist.tests.build_tests import module_test_helper


def _create_promotion_request(comment="Tested on all target platforms."):
    promotion_request = PromotionRequest(
        status="staged",
        comment=comment,
        ci_user="builder",
        timestamp="ISO8601",
        dry_run=True,
        target_repo="libs-release-local",
        copy=False,
        artifacts=True,
        dependencies=False,
        scopes=['compile', 'runtime'],
        properties={
            "components": ["c1", "c3", "c14"],
            "release-name": ["fb3-ga"]},
        fail_fast=True)
    return promotion_request


def equals_test():
    promotion_request = _create_promotion_request()
    promotion_requestB = _create_promotion_request()
    promotion_requestC = _create_promotion_request(comment="lets be different")

    eq_(promotion_request, promotion_requestB)
    assert promotion_requestC != promotion_request, "%r == %r" % (promotion_requestC, promotion_request)


def json_encoding_decoding_test():
    promotion_request = _create_promotion_request()

    def assert_expected_promotion_request(other):
        eq_(other, promotion_request)

    module_test_helper.round_trip_to_and_from_wire_format(
        promotion_request,
        PromotionRequest.from_json_data,
        assert_expected_promotion_request)


def typical_usage_test():
    expected_json_data = {
        "status": "staged",
        "comment": "Tested on all target platforms.",
        "ciUser": "builder",
        "timestamp": "ISO8601",
        "dryRun": True,
        "targetRepo": "libs-release-local",
        "copy": False,
        "artifacts": True,
        "dependencies": False,
        "scopes": ["compile", "runtime"],
        "properties": {
            "components": ["c1", "c3", "c14"],
            "release-name": ["fb3-ga"]},
        "failFast": True,
    }

    promotion_request = _create_promotion_request()

    actual_json_data = promotion_request.as_json_data

    eq_(actual_json_data, expected_json_data)


def no_scopes_specified_test():
    expected_json_data = {
        "status": "staged",
        "comment": "Tested on all target platforms.",
        "ciUser": "builder",
        "timestamp": "ISO8601",
        "dryRun": True,
        "targetRepo": "libs-release-local",
        "copy": False,
        "artifacts": True,
        "dependencies": False,
        "scopes": None,
        "properties": None,
        "failFast": True,
    }

    promotion_request = PromotionRequest(
        status="staged",
        comment="Tested on all target platforms.",
        ci_user="builder",
        timestamp="ISO8601",
        dry_run=True,
        target_repo="libs-release-local",
        copy=False,
        artifacts=True,
        dependencies=False,
        properties=None,
        fail_fast=True)

    actual_json_data = promotion_request.as_json_data

    eq_(actual_json_data, expected_json_data)
