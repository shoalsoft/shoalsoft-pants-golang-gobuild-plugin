# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.

from shoalsoft.pants_golang_gobuild_plugin.goals import check
from shoalsoft.pants_golang_gobuild_plugin.target_types import GoModuleTarget
from shoalsoft.pants_golang_gobuild_plugin.util_rules import go_bootstrap, goroot


def target_types():
    return (GoModuleTarget,)


def rules():
    return (
        *check.rules(),
        *go_bootstrap.rules(),
        *goroot.rules(),
    )
