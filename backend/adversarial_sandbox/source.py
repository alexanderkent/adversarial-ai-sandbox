import inspect
import textwrap
from .schema import CodeSnippet


def snippet(fn, label=None) -> CodeSnippet:
    """Return the real, current source of `fn` as a CodeSnippet (dedented, so methods
    render flush-left). Using inspect.getsource guarantees the displayed code matches
    what actually runs."""
    source = textwrap.dedent(inspect.getsource(fn)).strip("\n")
    return CodeSnippet(label=label or getattr(fn, "__name__", "code"), source=source)
