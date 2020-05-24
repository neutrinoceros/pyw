from pathlib import Path

import pytest  # type: ignore

from whych.api import WhychFinder


def test_unexisting_package():
    name = "NotARealPackage"
    wf = WhychFinder(name)
    assert wf.module_name == name
    assert wf.path is None
    assert wf.version is None

    assert wf.get_data() == {
        "module name": name,
        "path": "unknown",
        "version": "unknown",
    }


@pytest.mark.parametrize(
    "name",
    ["numpy", "matplotlib", "pandas", "requests", "django", "flask", "IPython", "tqdm"],
)
def test_common_third_party(name: str):
    pytest.importorskip(name)
    wf = WhychFinder(name)
    assert wf.module_name == name
    assert isinstance(wf.path, str)
    p = Path(wf.path)
    assert p.is_file()
    assert name in p.parts
