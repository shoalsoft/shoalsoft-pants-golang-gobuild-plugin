# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.

import io
import textwrap

import pytest

from pants.core.goals.check import CheckResults
from pants.engine.internals.native_engine import Address
from pants.testutil.rule_runner import QueryRule, RuleRunner
from shoalsoft.pants_golang_gobuild_plugin.goals.check import (
    GoCheckModuleFieldSet,
    GoCheckModuleRequest,
)
from shoalsoft.pants_golang_gobuild_plugin.register import rules as all_rules
from shoalsoft.pants_golang_gobuild_plugin.register import target_types


@pytest.fixture
def rule_runner() -> RuleRunner:
    rr = RuleRunner(
        rules=[
            *all_rules(),
            QueryRule(CheckResults, (GoCheckModuleRequest,)),
        ],
        target_types=target_types(),
    )
    rr.set_options(["--golang2-go-search-paths=['<PATH>']"], env_inherit={"PATH", "HOME"})
    return rr


def _compile(rule_runner: RuleRunner, address: Address) -> CheckResults:
    tgt = rule_runner.get_target(address)
    field_set = GoCheckModuleFieldSet.create(tgt)
    check_request = GoCheckModuleRequest(field_sets=[field_set])
    check_results = rule_runner.request(CheckResults, [check_request])
    return check_results


def _assert_results_success(check_results: CheckResults) -> None:
    if check_results.exit_code == 0:
        assert all(check_result.exit_code == 0 for check_result in check_results.results)
        return

    msg = io.StringIO()
    for check_result in check_results.results:
        msg.write(f"Compile: {check_result.partition_description}\n")
        msg.write(f"stdout:\n{check_result.stdout}\n")
        msg.write(f"stderr:\n{check_result.stderr}\n")

    raise AssertionError(f"Check was not successful.\n\n{msg.getvalue()}")


def test_build_go_module_success(rule_runner: RuleRunner) -> None:
    rule_runner.write_files(
        {
            "BUILD": "go_module(name='mod')\n",
            "go.mod": textwrap.dedent(
                """\
            module example.com/foo
            go 1.16
            """
            ),
            "foo.go": textwrap.dedent(
                """\
            package foo

            func Add(x int, y int) int {
                return x + y
            }
            """
            ),
        }
    )
    results = _compile(rule_runner, Address("", target_name="mod"))
    _assert_results_success(results)
