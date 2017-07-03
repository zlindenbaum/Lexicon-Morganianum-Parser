from pyparsing import Optional, Literal, OneOrMore, oneOf, alphanums, Or, Word, alphas8bit, nums, printables, SkipTo, LineStart, ZeroOrMore, LineEnd
import pprint as pp
import sys
import re
import unicodedata
# import pyparsing as pp

alphas = alphanums + alphas8bit


def Concat(parser): return parser.setParseAction(lambda x: " ".join(x))


def Cleanup(parser):
    return parser.setParseAction(lambda x: list(parsed.scanString(x))[0][0])


word_text = []

with open("../data/input.md", 'r') as input_doc:
    input_text = input_doc.read()
    with open("../data/output.md", 'a') as output_doc:
        print(len(input_text.split("\n")))
        for line in input_text.split("\n"):
            # print("Word " + str(i) + " --- " + line)
            line_p = line.replace("\xa0", " ")
            # line_p = unicodedata.normalize("NFC", line)
            word_text.append(line_p)

word_bold = (
    Literal("**").suppress() +
    Concat(OneOrMore(
        Word(alphas) ^
        Cleanup(Literal("(").suppress() + Word(alphas) + Literal(")").suppress())
    )) +
    Literal("**").suppress()
)

word_def = (
    LineStart() +
    Concat(SkipTo(Word("►¶"))).setResultsName("definition") +
    Literal("►").suppress() +
    Cleanup(SkipTo(Word("(|.¶")).setResultsName("words")) +
    ZeroOrMore(
        SkipTo(Word("►¶")).suppress() +
        Literal("►").suppress() +
        Concat(SkipTo(Word("(|.¶"))).setResultsName("words")
    ) +
    Optional(
        Literal("¶") +
        OneOrMore(
            Word("¶").suppress() +
            Concat(SkipTo(Word("¶") ^ LineEnd())).setResultsName("source")
        )
    )
)

parsed = Concat(
    SkipTo(Word(alphas)).suppress() +
    (
        word_bold ^
        OneOrMore(Word(alphas))
    )
)


def test(start, end):
    parsed_stuff = []
    for line in word_text[start:end]:
        parsed = list(word_def.scanString(line))
        if parsed != []:
            # print("yes")
            parsed_stuff.append(parsed)
         # else:
            # print("no")

    return parsed_stuff

def printTest(start, end):
    []
