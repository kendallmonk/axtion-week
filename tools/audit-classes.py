#!/usr/bin/env python3
"""Audit CSS classes in index.html.

There is no build step here, so nothing warns you when a rule stops being
used or when a new class silently collides with an existing one. That has
bitten this file for real: a `.dd` added for the day dots landed on top of
`.dd` (the domain description text) and squashed four paragraphs into 9px
circles, on desktop as well as mobile, and went unnoticed for a round.

Run this after touching styles or markup:

    python3 tools/audit-classes.py

Exits non-zero if anything is wrong, so it also works as a pre-commit hook.

Reports:
  UNUSED      rules defined in <style> that nothing references — dead weight
  UNDEFINED   classes used in markup or JS with no rule behind them — usually
              a typo or a rename that missed a spot
  SHORT       names too generic to be safe. A short name is fine when it is a
              namespace prefix with its own family (.blk -> .blk-name,
              .blk-detail); it is a hazard when it stands alone, because the
              next person to want two letters will take it.
  STRUCTURE   div balance and the presence of the password gate, as a cheap
              check that an edit did not truncate the file
"""

import re
import sys
from pathlib import Path

# Classes the scanner cannot see because they are assembled at runtime.
# Keep this list short, and say why each one is here.
DYNAMIC = {
    "sched-drop",  # built as "sched-" + button dataset.wk
    "sched-pick",
}

# Short names that are deliberate namespace prefixes, not standalone classes.
SHORT_OK = {"blk", "hdr"}

MAX_SHORT = 3


def classes_in_css(css: str) -> set:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)      # comments
    css = re.sub(r"@import[^;]+;", "", css)              # font URLs look like selectors
    selectors = re.sub(r"\{[^}]*\}", "", css)            # keep selectors, drop declarations
    return set(re.findall(r"\.([A-Za-z][\w-]*)", selectors))


def classes_in_markup(markup: str, whole_file: str) -> set:
    used = set()
    for attr in re.findall(r'class="([^"]*)"', markup):
        used.update(attr.split())
    used.update(re.findall(r'classList\.(?:add|remove|toggle)\("([\w-]+)"', whole_file))
    for sel in re.findall(r'querySelectorAll?\(\s*"([^"]+)"', whole_file):
        used.update(re.findall(r"\.([A-Za-z][\w-]*)", sel))
    return used


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else
                Path(__file__).resolve().parent.parent / "index.html")
    src = path.read_text(encoding="utf-8")

    style = re.search(r"<style>(.*?)</style>", src, re.S)
    if not style:
        print("FAIL: no <style> block found in %s" % path)
        return 1

    defined = classes_in_css(style.group(1))
    used = classes_in_markup(src[src.index("</style>"):], src) | DYNAMIC

    unused = sorted(defined - used)
    undefined = sorted(used - defined - DYNAMIC)
    short = sorted(n for n in (defined | used)
                   if len(n) <= MAX_SHORT and n not in SHORT_OK)

    opens = len(re.findall(r"<div\b", src))
    closes = len(re.findall(r"</div>", src))
    gated = "PASSWORD_HASH" in src and 'id="gate-lock"' in src

    print("%s — %d classes defined, %d used" % (path.name, len(defined), len(used)))
    print()
    print("UNUSED     %s" % (", ".join(unused) if unused else "none"))
    print("UNDEFINED  %s" % (", ".join(undefined) if undefined else "none"))
    print("SHORT      %s" % (", ".join(short) if short else "none"))
    print("STRUCTURE  %d <div> / %d </div>%s | gate %s"
          % (opens, closes,
             "" if opens == closes else "  <-- UNBALANCED",
             "present" if gated else "MISSING"))

    problems = []
    if undefined:
        problems.append("%d undefined class(es)" % len(undefined))
    if short:
        problems.append("%d unsafely short name(s)" % len(short))
    if opens != closes:
        problems.append("unbalanced divs")
    if not gated:
        problems.append("password gate missing")

    # Dead rules are worth knowing about but are not a failure on their own.
    if problems:
        print()
        print("FAIL: " + "; ".join(problems))
        return 1

    print()
    print("OK" + ("  (%d dead rule(s) worth pruning)" % len(unused) if unused else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
