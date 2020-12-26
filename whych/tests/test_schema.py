import platform
from pathlib import Path

import pytest
from schema import Optional, Schema

from whych.api import Importable

template = Schema(
    {
        "is_available": bool,
        "is_stdlib": bool,
        "member": str,
        "package_name": str,
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
    data = Importable(name)
    template.validate(data)


def test_empty_module_query(shared_datadir, monkeypatch):
    """Check for robustness of Importable()
    with an empty module (in particular, no version data)
    """
    fake_module = shared_datadir / "fake_empty_module"
    syspath, name = fake_module.parent, fake_module.name
    monkeypatch.syspath_prepend(syspath)

    data = Importable(name)
    assert Path(syspath, name) in Path(data["path"]).parents
    assert "version" not in data

    template.validate(data)


def test_field_member():
    d1 = Importable("os.path")
    d2 = Importable("os.path.expanduser")

    template.validate(d1)
    template.validate(d2)

    if platform.system() != "Windows":
        assert d2["module_name"] == d1["module_name"] == "posixpath"
    assert d2["version"] == d1["version"]
    assert d2["is_stdlib"] is d1["is_stdlib"] is True


def test_compiled_stdlib_member():
    Importable("math.sqrt")
