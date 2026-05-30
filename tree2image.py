#!/usr/bin/env python
#
# Natural Language Toolkit: tree->image rendering script
#

import os
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter.font

from nltk.draw.tree import TreeSegmentWidget
from nltk.draw.util import CanvasFrame, SequenceWidget, SpaceWidget, TextWidget

GS = shutil.which("gs") or "gs"
PS2PDF = shutil.which("ps2pdf") or "ps2pdf"

if "/sw/bin" not in os.environ.get("PATH", ""):
    os.environ["PATH"] = os.environ.get("PATH", "") + ":/sw/bin"


def tokenize(s, regexp):
    pos = 0
    for m in re.finditer(regexp, s):
        if m.start() != pos:
            raise ValueError("tokenization error")
        pos = m.end()
        yield m.group()


def tree_to_widget(s, canvas):
    WORD = r"(\\\\|\\[^\\\n]|[^\\\s()<>])+"
    TOKEN_RE = re.compile(r"\(\s*%s|<\s*%s|\)|>|%s|\s+" % (WORD, WORD, WORD))
    stack = [[]]
    for tok in tokenize(s.strip(), TOKEN_RE):
        if tok.strip() == "":
            pass
        elif tok[:1] in "(<":
            label = word_to_widget(tok[1:].strip(), canvas, color="#004080", bold=True)
            roof = tok[:1] == "<"
            stack[-1].append(dict(canvas=canvas, label=label, roof=roof))
            stack.append([])
        elif tok[:1] in ")>":
            subtrees = stack.pop()
            node_kwargs = stack[-1][-1]
            stack[-1][-1] = TreeSegmentWidget(subtrees=subtrees, **node_kwargs)
        else:
            leaf = word_to_widget(tok.strip(), canvas, color="#008040")
            stack[-1].append(leaf)

    if not len(stack) == 1 and len(stack[0]) == 1:
        raise ValueError("unbalanced parens?")
    return stack[0][0]


def parse_word(s):
    italic = False
    subscript = False
    piece = ""

    for tok in tokenize(s, r"\*|_{|}|_[^{]|\\.|[^\\_\*]"):
        if tok == "*":
            yield italic, subscript, piece
            italic = not italic
            piece = ""
        elif tok == "_{":
            yield italic, subscript, piece
            if subscript:
                raise ValueError("nested italics?")
            subscript = True
            piece = ""
        elif tok.startswith("_"):
            yield italic, subscript, piece
            if subscript:
                raise ValueError("nested italics?")
            yield italic, True, tok[1]
            piece = ""
        elif tok == "}":
            yield italic, subscript, piece
            if not subscript:
                raise ValueError("} needs backslash")
            subscript = False
            piece = ""
        else:
            piece += tok

    if italic:
        raise ValueError("expected * to close italics")
    if subscript:
        raise ValueError("expected }")
    yield italic, subscript, piece


metrics = {}


def word_to_widget(s, canvas, basefont="helvetica", fontsize=12, color="black", bold=False):
    textwidgets = []

    for (italic, subscript, text) in parse_word(s):
        if not text:
            continue
        text = re.sub(r"\\(.)", r"\1", text)
        size = fontsize
        if subscript:
            size = size * 2 / 3
        slant = "italic" if italic else "roman"
        weight = "bold" if bold else "normal"
        font = tkinter.font.Font(family=basefont, size=size, weight=weight, slant=slant)
        textwidgets.append(TextWidget(canvas, text, font=font, color=color))
        metrics[basefont, size, weight, slant] = font.metrics()

    if len(textwidgets) == 0:
        w = SpaceWidget(canvas, 1, 1)
        w.set_width(0)
        w.set_height(0)
        return w
    if len(textwidgets) == 1:
        return textwidgets[0]
    return SequenceWidget(canvas, *textwidgets, align="bottom", space=-2)


try:
    _canvas_frame
except NameError:
    _canvas_frame = None


def tree_to_ps(s, outfile):
    global _canvas_frame
    if _canvas_frame is None:
        _canvas_frame = CanvasFrame()

    widget = tree_to_widget(s, _canvas_frame.canvas())

    _canvas_frame.canvas()["scrollregion"] = (0, 0, 1, 1)
    _canvas_frame.add_widget(widget)
    _canvas_frame.print_to_file(outfile)
    bbox = widget.bbox()
    _canvas_frame.destroy_widget(widget)

    return bbox[2:]


def run(cmd):
    subprocess.check_call(cmd)


def convert_ps_to_png(psfile, outfile, density):
    run([
        GS,
        "-dSAFER",
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pngalpha",
        f"-r{density}",
        f"-sOutputFile={outfile}",
        psfile,
    ])


def convert_ps_to_pdf(psfile, outfile):
    run([
        PS2PDF,
        psfile,
        outfile,
    ])


def tree_to_image(s, outfile, density=72):
    cachefile = os.path.join(os.path.split(outfile)[0], "treecache.pickle")
    if os.path.exists(cachefile):
        try:
            with open(cachefile, "rb") as fh:
                cache = pickle.load(fh)
            if cache.get(outfile, None) == (s, density):
                return
        except Exception:
            cache = {}
    else:
        cache = {}

    fd, psfile = tempfile.mkstemp(suffix=".ps")
    os.close(fd)

    try:
        tree_to_ps(s, psfile)

        if outfile.endswith(".ps"):
            shutil.copyfile(psfile, outfile)
        elif outfile.endswith(".png"):
            convert_ps_to_png(psfile, outfile, density)
        elif outfile.endswith(".pdf"):
            convert_ps_to_pdf(psfile, outfile)
        else:
            raise ValueError(f"unsupported output format: {outfile}")

    finally:
        if os.path.exists(psfile):
            os.remove(psfile)

    cache[outfile] = (s, density)
    with open(cachefile, "wb") as out:
        pickle.dump(cache, out)


def cli():
    if len(sys.argv) != 3:
        print("Usage: %s <infile> <outfile>" % sys.argv[0])
        sys.exit(-1)
    print("%s -> %s" % (sys.argv[1], sys.argv[2]))
    with open(sys.argv[1], encoding="utf-8") as fh:
        tree_to_image(fh.read(), sys.argv[2])


if __name__ == "__main__":
    cli()
