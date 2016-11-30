import random

random.seed(0)

import script
import grammar
import translation
import poem
import re
import sys


npoems = int(sys.argv[1])
vocabsofar = set()


def fixfootnotes(text):
    footnotes = []

    def replace(s):
        s = s.group(0)
        footnotes.append(s[10:-1])
        return "\\footnotemark"

    text = re.sub(r"\\footnote{[^}]*}", replace, text)
    for f in footnotes:
        text += "\\footnotetext{%s}" % f
    return text

def linecount(pos):
    return sum(random.random() < pos for _ in range(6)) + 3

meanings = 0

print("Generating %d poems" % npoems)
with open("book/poems.tex", "w") as tex:
    for i in range(npoems):
        nlines = linecount(i / npoems)
        print("Generating poem %d with %d lines" % (i+1, nlines))
        p = poem.Poem(nlines)
        vocab = set(p.words)
        newvocab = vocab - vocabsofar
        vocabsofar |= vocab
        tex.write("\\chapter{%s}\n\n" % grammar.flatten("#poemtitle#"))

        s = script.renderpoem(p.lines)
        filename = "book/poem%02d.pdf" % i
        s.savepdf(filename)
        tex.write("\\begin{center}\n"
                  "\\includegraphics[scale=0.8]{%s}\n\\end{center}\n\n" %
                  filename)

        tex.write(grammar.lookup("pieceintro") + "\n\n")
        tex.write("\\section{Transcription}\n")

        for line in p.lines:
            tex.write(" ".join(line) + "\\\\\n")
        tex.write("\n\n")

        tex.write("\\section{Gloss}\n\n")
        gloss = [g if g else "[...]" for g in p.gloss()]
        tex.write(" ".join(gloss) + "\n\n")

        if newvocab:
            tex.write("\section{Vocabulary}\n\n")
            for w in sorted(newvocab):
                filename = "book/%s.pdf" % w
                script.renderglyph(w).savepdf(filename)
                tex.write("\\noindent\\parbox{0.18\\textwidth}"
                          "{\\includegraphics[scale=0.8]{%s}}\n" % filename)

                readings = translation.gloss(w)
                random.shuffle(readings)
                trans = ''
                for reading in readings:
                    if not trans:
                        trans = grammar.lookup("gloss1", reading=reading,
                                also="")
                    else:
                        trans += ' ' + grammar.lookup(
                            "gloss2", reading=reading, also=" also")
                if not readings:
                    trans = "The correct reading of this glyph is unknown."
                else:
                    meanings += 1
                tex.write(
                    fixfootnotes("\\parbox{0.8\\textwidth}{\\emph{%s} %s}" % (
                        w, trans)) + "\\vspace{1em}\n\n")

print("%d vocab items, %d with definitions" % (len(vocabsofar), meanings))
