"""Run player-written Python safely enough for a village ward puzzle.

The player's code is real Python, so there is no custom interpreter to port.
Safety here is scoped to what Tier 1 needs: a restricted builtin set, captured
stdout, and a wall-clock timeout. This is a game, not a hardened sandbox.
"""

import io
import sys
import time
import traceback
from contextlib import redirect_stdout

MAX_CODE_CHARS = 6000


class _RunTimeout(Exception):
    pass


if sys.platform != "win32":
    import signal

    def _timeout_handler(signum, frame):
        raise _RunTimeout()

    HAVE_SIGNAL = True
else:
    HAVE_SIGNAL = False


class _Deadline:
    """Wall-clock guard for platforms without SIGALRM (Windows).

    ``sys.settrace`` inspects every line the spell executes, so an
    infinite ``while True:`` raises ``_RunTimeout`` instead of freezing
    the window. Tracing roughly doubles the cost of the script, so the
    guard gets twice the budget it enforces.
    """

    def __init__(self, seconds):
        self.deadline = time.monotonic() + seconds * 2.0
        self._ticks = 0

    def __call__(self, frame, event, arg):
        self._ticks += 1
        if self._ticks >= 2000:            # read the clock sparingly
            self._ticks = 0
            if time.monotonic() >= self.deadline:
                raise _RunTimeout()
        return self


# Tier 1 vocabulary. Everything the design doc teaches (variables, print,
# if/else, for, functions) works with just these.
SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "round": round,
    "sorted": sorted,
    "reversed": reversed,
    "enumerate": enumerate,
    "zip": zip,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "any": any,
    "all": all,
    "True": True,
    "False": False,
    "None": None,
    # error handling and little classes are medium-Python lessons,
    # so the ward permits catching errors and building classes
    "__build_class__": __build_class__,
    "Exception": Exception,
    "TypeError": TypeError,
    "ValueError": ValueError,
    "NameError": NameError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "AttributeError": AttributeError,
    "ZeroDivisionError": ZeroDivisionError,
}


def _fail(output, message, line):
    return {"ok": False, "output": output, "env": None, "line": line, "message": message}


def run_code(code, env=None, timeout=2.0):
    """Execute player code.

    Returns a dict with:
      ok      -> bool
      output  -> captured stdout (str)
      env     -> the resulting scope (on success)
      line    -> 1-based source line of an error, or -1
      message -> short human-readable error text
    """
    if len(code) > MAX_CODE_CHARS:
        return _fail("", "The runes run off the tablet — that is far too much script.", -1)

    if not code.strip():
        return _fail("", "The tablet waits. There is nothing written to run.", -1)

    env = {} if env is None else dict(env)
    env["__builtins__"] = SAFE_BUILTINS
    env.setdefault("__name__", "__main__")
    env.setdefault("__file__", "<tablet>")

    buf = io.StringIO()
    try:
        if HAVE_SIGNAL:
            old = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, timeout)
            try:
                with redirect_stdout(buf):
                    compiled = compile(code, "<tablet>", "exec")
                    exec(compiled, env, env)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)
        else:
            # Windows: no SIGALRM, so watch the clock line by line
            guard = _Deadline(timeout)
            sys.settrace(guard)
            try:
                with redirect_stdout(buf):
                    compiled = compile(code, "<tablet>", "exec")
                    exec(compiled, env, env)
            finally:
                sys.settrace(None)
        return {"ok": True, "output": buf.getvalue(), "env": env, "line": -1, "message": ""}
    except _RunTimeout:
        return _fail(buf.getvalue(), "That spell is taking too long to cast — it looped forever.", -1)
    except SyntaxError as e:
        line = e.lineno or 1
        msg = e.msg or "Bad syntax"
        return _fail(buf.getvalue(), "%s (line %s)" % (msg, line), line)
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line = -1
        for frame in reversed(tb):
            if frame.filename == "<tablet>":
                line = frame.lineno
                break
        return _fail(buf.getvalue(), "%s: %s" % (type(e).__name__, e), line)
