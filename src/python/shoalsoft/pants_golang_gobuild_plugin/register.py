# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.

from shoalsoft.pants_golang_gobuild_plugin.goals import check, tailor
from shoalsoft.pants_golang_gobuild_plugin.target_types import GoModuleTarget
from shoalsoft.pants_golang_gobuild_plugin.util_rules import binary, go_bootstrap, goroot


def target_types():
    return (GoModuleTarget,)


def rules():
    return (
        *binary.rules(),
        *check.rules(),
        *go_bootstrap.rules(),
        *goroot.rules(),
        *tailor.rules(),
    )
