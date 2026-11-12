"""The rune tablets: every stop teaches one small Python spell.

This is the coding heart of the game. Each stop carries a ``code``
puzzle spec (written in ``story.py`` next to its dialogue), and this
module checks the player's script against it. Five archetypes cover
the whole teaching arc from Act 1's first ``print`` to Act 3's little
functions:

  say    the script's last printed line must equal ``expect``
  lines  the script's printed lines must equal ``expect`` exactly
  set    the variable ``var`` must equal ``expect`` after the run
  table  the script runs once per case ``[(env, expect), ...]`` and
         every run's last printed line must match
  func   the defined function ``name`` is called with ``calls``
         ``[(args, expect), ...]`` and every return must match
  safe   like func, but ``traps`` ``[(args, expect), ...]`` must be
         survived without raising (the try/except lesson)
  class  the defined class ``name`` is built with ``make`` args, then
         ``checks`` run: ("attr", name, expect) and ("call", method,
         args, expect)

Every failure answers with the ward's voice plus the puzzle's own
hint, so a stuck player is taught, never mocked.
"""

from .runner import run_code


def validate(spec, code):
    """Check player ``code`` against a puzzle ``spec``.

    Returns ``(ok, console, status)`` for the tablet to display.
    """
    kind = spec.get("kind", "say")
    if kind == "say":
        return _validate_say(spec, code)
    if kind == "lines":
        return _validate_lines(spec, code)
    if kind == "set":
        return _validate_set(spec, code)
    if kind == "table":
        return _validate_table(spec, code)
    if kind == "func":
        return _validate_func(spec, code)
    if kind == "safe":
        return _validate_safe(spec, code)
    if kind == "class":
        return _validate_class(spec, code)
    if kind == "gauntlet":
        return _validate_gauntlet(spec, code)
    return False, "The tablet does not know this spell.", _hint(spec)


def _hint(spec):
    return spec.get("hint", "Read the tablet's status. The words say the rule.")


def _fail_line(result):
    if result["line"] > 0:
        return "The ward sputters at rune %d — %s" % (result["line"], result["message"])
    return "The ward sputters — %s" % result["message"]


def _last_line(output):
    lines = output.strip().split("\n")
    return lines[-1] if lines and lines != [""] else ""


def _validate_say(spec, code):
    result = run_code(code, dict(spec.get("env", {})))
    if not result["ok"]:
        return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
    got = _last_line(result["output"])
    if got != spec["expect"]:
        return False, "it ends: %s" % (got or "(silence)"), (
            "The ward waits for it to end on \"%s\"." % spec["expect"]
            + "\n\n" + _hint(spec))
    return True, "The runes hold steady.", spec.get("praise", "It holds. Well written.")


def _validate_lines(spec, code):
    result = run_code(code, dict(spec.get("env", {})))
    if not result["ok"]:
        return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
    got = [line for line in result["output"].strip().split("\n")] if result["output"].strip() else []
    if got != list(spec["expect"]):
        shown = ", ".join(got[:6]) or "(silence)"
        return False, "it chants: %s" % shown, (
            "The ward wants %d lines, in order: %s." % (
                len(spec["expect"]), ", ".join(spec["expect"]))
            + "\n\n" + _hint(spec))
    return True, "The runes hold steady.", spec.get("praise", "Every line in its place.")


def _validate_set(spec, code):
    result = run_code(code, dict(spec.get("env", {})))
    if not result["ok"]:
        return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
    var = spec["var"]
    got = result["env"].get(var, "<missing>")
    if got != spec["expect"]:
        return False, "%s is %r" % (var, got), (
            "The ward wants %s to hold %r." % (var, spec["expect"])
            + "\n\n" + _hint(spec))
    return True, "The runes hold steady.", spec.get("praise", "%s settles into place." % var)


def _validate_table(spec, code):
    var = spec["var"]
    for value, expect in spec["cases"]:
        result = run_code(code, {var: value})
        if not result["ok"]:
            return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
        got = _last_line(result["output"])
        if got != expect:
            return False, "%s = %r → ends: %s" % (var, value, got or "(silence)"), (
                "With %s = %r the ward wants it to end on \"%s\"."
                % (var, value, expect) + "\n\n" + _hint(spec))
    return True, "Every case holds true.", spec.get("praise", "True in every weather.")


def _validate_func(spec, code):
    result = run_code(code)
    if not result["ok"]:
        return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
    name = spec["name"]
    fn = result["env"].get(name)
    if not callable(fn):
        return False, "no spell named %s" % name, (
            "The ward wants a function called %s." % name + "\n\n" + _hint(spec))
    for args, expect in spec["calls"]:
        try:
            got = fn(*args)
        except Exception as exc:  # noqa: BLE001 - player code can raise anything
            return False, "%s%r raised %s" % (name, tuple(args), type(exc).__name__), (
                "The ward calls %s%r and it stumbles." % (name, tuple(args))
                + "\n\n" + _hint(spec))
        if got != expect:
            return False, "%s%r gave %r" % (name, tuple(args), got), (
                "The ward wants %s%r to give %r." % (name, tuple(args), expect)
                + "\n\n" + _hint(spec))
    return True, "Every calling holds true.", spec.get("praise", "Called, and answered.")


def _validate_safe(spec, code):
    """A function that must also survive bad input (try/except)."""
    result = run_code(code)
    if not result["ok"]:
        return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
    name = spec["name"]
    fn = result["env"].get(name)
    if not callable(fn):
        return False, "no spell named %s" % name, (
            "The ward wants a function called %s." % name + "\n\n" + _hint(spec))
    for args, expect in spec.get("calls", []):
        try:
            got = fn(*args)
        except Exception as exc:  # noqa: BLE001
            return False, "%s%r raised %s" % (name, tuple(args), type(exc).__name__), (
                "The ward calls %s%r and it stumbles." % (name, tuple(args))
                + "\n\n" + _hint(spec))
        if got != expect:
            return False, "%s%r gave %r" % (name, tuple(args), got), (
                "The ward wants %s%r to give %r." % (name, tuple(args), expect)
                + "\n\n" + _hint(spec))
    for args, expect in spec.get("traps", []):
        try:
            got = fn(*args)
        except Exception as exc:  # noqa: BLE001
            return False, "%s%r raised %s" % (name, tuple(args), type(exc).__name__), (
                "Bad weather broke it! Catch the error with try/except and "
                "answer %r instead." % (expect,) + "\n\n" + _hint(spec))
        if got != expect:
            return False, "%s%r gave %r" % (name, tuple(args), got), (
                "Rough input still owes %r." % (expect,) + "\n\n" + _hint(spec))
    return True, "Fair weather or foul, it holds.", spec.get("praise", "Stormproof.")


def _validate_class(spec, code):
    """A little class, built and questioned."""
    result = run_code(code)
    if not result["ok"]:
        return False, "The ward sputters.", _fail_line(result) + "\n\n" + _hint(spec)
    name = spec["name"]
    cls = result["env"].get(name)
    if not isinstance(cls, type):
        return False, "no craft named %s" % name, (
            "The ward wants a class called %s." % name + "\n\n" + _hint(spec))
    try:
        obj = cls(*spec.get("make", []))
    except Exception as exc:  # noqa: BLE001
        return False, "%s() raised %s" % (name, type(exc).__name__), (
            "The ward builds %s() and it stumbles." % name + "\n\n" + _hint(spec))
    for check in spec.get("checks", []):
        if check[0] == "attr":
            __, attr, expect = check
            got = getattr(obj, attr, "<missing>")
            if got != expect:
                return False, "%s.%s is %r" % (name, attr, got), (
                    "The ward wants %s.%s to hold %r." % (name, attr, expect)
                    + "\n\n" + _hint(spec))
        elif check[0] == "call":
            __, method, args, expect = check
            fn = getattr(obj, method, None)
            if not callable(fn):
                return False, "%s has no %s" % (name, method), (
                    "The ward wants %s to answer %s." % (name, method)
                    + "\n\n" + _hint(spec))
            try:
                got = fn(*args)
            except Exception as exc:  # noqa: BLE001
                return False, "%s.%s raised %s" % (name, method, type(exc).__name__), (
                    "The ward calls it and it stumbles." + "\n\n" + _hint(spec))
            if got != expect:
                return False, "%s.%s gave %r" % (name, method, got), (
                    "The ward wants %r." % (expect,) + "\n\n" + _hint(spec))
    return True, "Built, questioned, true.", spec.get("praise", "A fine craft.")


def _validate_gauntlet(spec, code):
    """A boss tablet: every part must hold in the same script."""
    notes = []
    for i, part in enumerate(spec["parts"]):
        ok, console, _status = validate(part, code)
        notes.append("spell %d: %s" % (i + 1, console))
        if not ok:
            return False, "\n".join(notes), (
                "The boss tablet wants every spell at once (%d of %d hold)."
                % (i, len(spec["parts"])) + "\n\n" + _hint(spec))
    return True, "\n".join(notes), spec.get("praise", "Every spell holds. Boss beaten.")


def solution_hint(spec):
    """One-line shape of the answer, for tests and debugging."""
    kind = spec.get("kind", "say")
    if kind == "say":
        return 'print("%s")' % spec["expect"]
    if kind == "lines":
        return "print each of %s" % (spec["expect"],)
    if kind == "set":
        return '%s = %r' % (spec["var"], spec["expect"])
    if kind == "table":
        return "if/else on %s" % spec["var"]
    if kind == "func":
        return "def %s(...)" % spec["name"]
    if kind == "safe":
        return "def %s(...) that survives storms" % spec["name"]
    if kind == "class":
        return "class %s(...)" % spec["name"]
    if kind == "gauntlet":
        return "boss: %d spells in one script" % len(spec.get("parts", []))
    return "?"
