"""Write an intersphinx inventory to the site, so Sphinx projects can link to the Reacton API docs."""

import re
import zlib
from pathlib import Path

HEADER = b"""# Sphinx inventory version 2
# Project: Reacton
# Version: latest
# The remainder of this file is compressed using zlib.
"""


def inventory_body(api_markdown: str) -> bytes:
    # each "#### name" heading in docs/api.md documents one function
    names = sorted(re.findall(r"^#### (\w+)$", api_markdown, re.MULTILINE))
    if not names:
        raise ValueError("Found no API headings in docs/api.md")
    lines = [f"{module}.{name} py:function 1 api/#{name} -\n" for name in names for module in ["reacton", "reacton.core"]]
    return "".join(lines).encode("utf8")


def on_post_build(config, **kwargs):
    api_markdown = (Path(config["docs_dir"]) / "api.md").read_text(encoding="utf8")
    output = Path(config["site_dir"]) / "objects.inv"
    output.write_bytes(HEADER + zlib.compress(inventory_body(api_markdown), 9))
