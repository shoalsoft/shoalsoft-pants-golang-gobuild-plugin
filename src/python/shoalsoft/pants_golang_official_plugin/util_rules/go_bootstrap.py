# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Collection

from pants.core.util_rules import search_paths
from pants.core.util_rules.search_paths import ValidatedSearchPaths, ValidateSearchPathsRequest
from pants.engine.env_vars import PathEnvironmentVariable
from pants.engine.internals.selectors import Get
from pants.engine.rules import collect_rules, rule
from pants.util.ordered_set import FrozenOrderedSet
from shoalsoft.pants_golang_official_plugin.subsystems.golang import GolangSubsystem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GoBootstrap:
    go_search_paths: tuple[str, ...]


async def _go_search_paths(
    paths: Collection[str],
) -> tuple[str, ...]:
    path_variables = await Get(PathEnvironmentVariable)
    expanded: list[str] = []
    for s in paths:
        if s == "<PATH>":
            expanded.extend(path_variables)
        else:
            expanded.append(s)
    return tuple(expanded)


@rule
async def resolve_go_bootstrap(
    golang_subsystem: GolangSubsystem,
    golang_env_aware: GolangSubsystem.EnvironmentAware,
) -> GoBootstrap:
    search_paths = await Get(
        ValidatedSearchPaths,
        ValidateSearchPathsRequest(
            env_tgt=golang_env_aware.env_tgt,
            search_paths=tuple(golang_env_aware.raw_go_search_paths),
            option_origin=f"[{GolangSubsystem.options_scope}].go_search_paths",
            environment_key="golang_go_search_paths",
            is_default=golang_env_aware._is_default("_go_search_paths"),
            local_only=FrozenOrderedSet(),
        ),
    )
    paths = await _go_search_paths(search_paths)

    return GoBootstrap(go_search_paths=paths)


def compatible_go_version(*, compiler_version: str, target_version: str) -> bool:
    """Can the Go compiler handle the target version?

    Inspired by
    https://github.com/golang/go/blob/30501bbef9fcfc9d53e611aaec4d20bb3cdb8ada/src/cmd/go/internal/work/exec.go#L429-L445.

    Input expected in the form `1.17`.
    """
    if target_version == "1.0":
        return True

    def parse(v: str) -> tuple[int, int]:
        parts = v.split(".", maxsplit=2)
        major, minor = parts[0], parts[1]
        return int(major), int(minor)

    return parse(target_version) <= parse(compiler_version)


def rules():
    return (
        *collect_rules(),
        *search_paths.rules(),
    )
