from pyparsing import Optional, Literal, OneOrMore, oneOf, alphanums, Or, Word, alphas8bit, nums, printables, SkipTo, LineStart, ZeroOrMore, LineEnd, Group
import pprint as pp
import sys
import re
import unicodedata
import json
# import pyparsing as pp

alphas = alphanums + alphas8bit
genders = "m. n. f. pl."


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


word_def = (
    LineStart() +
    Concat(SkipTo(Word("►¶"))).setResultsName("definition") +
    OneOrMore(
        Literal("►").suppress() +
        Concat(SkipTo(
            oneOf(genders) ^
            Word("|.¶")
        )).setResultsName("words") +
        Optional(oneOf(genders).setResultsName("gender"), default="UNKNOWN") +

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
    ldict = locals()
    exec("p_list = " + repr(parsed), globals(), ldict) #because pyparsing is stupid
    p_list = ldict['p_list']

    # pp.pprint(p_list)
    return {
        'definition': p_list[1]['definition'],
        'words': [
            {'word': a, 'source': b, 'gender': c} for (a, b, c) in
            list(zip(p_list[1]['words'], p_list[1]['sources'], p_list[1]['gender']))
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
