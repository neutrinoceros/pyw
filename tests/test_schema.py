import platform
from pathlib import Path

import pytest
from schema import Optional, Schema

from pyw.api import Scope

template = Schema(
    {
        "is_available": bool,
        "is_stdlib": bool,
        "package_name": str,
        "scope_name": str,
        Optional("module_name"): str,
        Optional("is_module"): bool,
        Optional("path"): str,
        Optional("version"): str,
        Optional("last_updated"): str,
        Optional("git_hash"): str,
        Optional("line"): int,
    }
)


@pytest.mark.parametrize("name", ["NotARealPackage", "os.path.NotARealMember"])
def test_non_existing_member(name):
    data = Scope(name)
    template.validate(data)


def test_empty_module_query(shared_datadir, monkeypatch):
    """Check for robustness of Scope()
    with an empty module (in particular, no version data)
    """
    fake_module = shared_datadir / "fake_empty_module"
    syspath, name = fake_module.parent, fake_module.name
    monkeypatch.syspath_prepend(syspath)

    data = Scope(name)
    assert Path(syspath, name) in Path(data["path"]).parents
    assert "version" not in data

    template.validate(data)


def test_field_member():
    d1 = Scope("os.path")
    d2 = Scope("os.path.expanduser")

    template.validate(d1)
    template.validate(d2)

    if platform.system() != "Windows":
        assert d2["module_name"] == d1["module_name"] == "posixpath"
    assert d2["version"] == d1["version"]
    assert d2["is_stdlib"] is d1["is_stdlib"] is True


def test_compiled_stdlib_member():
    Scope("math.sqrt")
