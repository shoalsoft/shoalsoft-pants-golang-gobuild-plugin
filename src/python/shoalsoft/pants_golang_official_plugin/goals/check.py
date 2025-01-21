# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.


import os
from dataclasses import dataclass

from pants.core.goals.check import CheckRequest, CheckResult, CheckResults
from pants.engine.env_vars import EnvironmentVars, EnvironmentVarsRequest
from pants.engine.intrinsics import execute_process
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessCacheScope, ProcessExecutionEnvironment
from pants.engine.rules import Get, collect_rules, concurrently, rule
from pants.engine.target import FieldSet
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from shoalsoft.pants_golang_official_plugin.target_types import GoModSourceField
from shoalsoft.pants_golang_official_plugin.util_rules import goroot
from shoalsoft.pants_golang_official_plugin.util_rules.goroot import GoRoot


@dataclass(frozen=True)
class GoCheckModuleFieldSet(FieldSet):
    required_fields = (GoModSourceField,)


class GoCheckModuleRequest(CheckRequest):
    field_set_type = GoCheckModuleFieldSet
    tool_name = "go-compile"


def _process_for_compilation(
    field_set: GoCheckModuleFieldSet, goroot: GoRoot, env_vars: EnvironmentVars
) -> Process:
    spec_path = field_set.address.spec_path

    process = Process(
        argv=[os.path.join(goroot.path, "bin", "go"), "build", f"./{spec_path}"],
        description=f"Compile Go module at {spec_path}",
        cache_scope=ProcessCacheScope.PER_SESSION,
        env=env_vars,
    )

    return process


@rule(desc="Check Go compilation", level=LogLevel.DEBUG)
async def check_go_module(
    request: GoCheckModuleRequest, goroot: GoRoot, platform: Platform
) -> CheckResults:
    process_execution_environment = ProcessExecutionEnvironment(
        environment_name=None,
        platform=platform.value,
        docker_image=None,
        remote_execution=False,
        remote_execution_extra_platform_properties=(),
        execute_in_workspace=True,
    )

    env_vars = await Get(
        EnvironmentVars, EnvironmentVarsRequest(["PATH", "HOME"], allowed=["PATH", "HOME"])
    )

    processes = [
        _process_for_compilation(field_set, goroot=goroot, env_vars=env_vars)
        for field_set in request.field_sets
    ]

    results = await concurrently(
        (execute_process(process, process_execution_environment) for process in processes)
    )

    check_results = [
        CheckResult(
            result.exit_code,
            stdout=result.stdout.decode(errors="replace"),
            stderr=result.stderr.decode(errors="replace"),
        )
        for result in results
    ]

    return CheckResults(check_results, checker_name=request.tool_name)


def rules():
    return (
        *collect_rules(),
        *goroot.rules(),
        UnionRule(CheckRequest, GoCheckModuleRequest),
    )
