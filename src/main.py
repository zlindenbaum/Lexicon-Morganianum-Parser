from pyparsing import Optional, Literal, OneOrMore, oneOf, alphanums, Or, Word, alphas8bit, nums, printables, SkipTo, LineStart, ZeroOrMore, LineEnd, Group
import pprint as pp
import sys
import re
import unicodedata
import json
# import pyparsing as pp

alphas = alphanums + alphas8bit


def Concat(parser): return parser.setParseAction(lambda x: " ".join(x))


def Cleanup(parser):
    return parser.setParseAction(lambda x: list(parsed.scanString(x))[0][0])


word_text = []

with open("../data/input.md", 'r') as input_doc:
    input_text = input_doc.read()
    with open("../data/output.md", 'w') as output_doc:
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


#TODO: put lineEnd in word parser
word_def = (
    LineStart() +
    Concat(SkipTo(Word("►¶"))).setResultsName("definition") +
    OneOrMore(
        Literal("►").suppress() +
        Concat(SkipTo(Word("|.¶"))).setResultsName("words") +

        SkipTo(Literal("¶")).suppress() +
        Literal("¶").suppress() +
        Concat(SkipTo(Literal("►") ^ LineEnd())).setResultsName("sources") +
        SkipTo(Word("►¶")).suppress()
    )
)

parsed = Concat(
    SkipTo(Word(alphas)).suppress() +
    (
        word_bold ^
        OneOrMore(Word(alphas))
    )
)


def process_parsed(parsed):
    # p_list = []

    ldict = locals()
    exec("p_list = " + repr(parsed), globals(), ldict)

    p_list = ldict['p_list']

    # pp.pprint(p_list)
    return {
        'definition': p_list[1]['definition'],
        'words': [
            {'word': a, 'source': b} for (a, b) in
            list(zip(p_list[1]['words'], p_list[1]['sources']))
        ]
    }


def test(start, end):
    parsed_stuff = []
    for line in word_text[start:end]:
        try:
            parsed = word_def.parseString(line)
            parsed_stuff.append(process_parsed(parsed))
        except:
            pass

    return parsed_stuff


def write(start, end):
    with open("../data/output.json", 'w') as output_json:
        json.dump(test(start, end), output_json)
