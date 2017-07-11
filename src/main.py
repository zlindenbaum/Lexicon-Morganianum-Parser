from pyparsing import Optional, Literal, OneOrMore, oneOf, alphanums, Or, Word, alphas8bit, nums, printables, SkipTo, LineStart, ZeroOrMore, LineEnd, Group, NotAny
import pprint as pp
import sys
import re
import unicodedata
import json
# import pyparsing as pp

alphas = alphanums + alphas8bit
genders = "m. n. f. pl. m.pl. n.pl. f.pl. indecl."
word_types = "adj. vb. n."


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
    Optional(Word(nums + " /")).suppress() +
    Concat(SkipTo(Word("►¶"))).setResultsName("definition") +
    OneOrMore(
        Literal("►").suppress() +
        NotAny(Literal("►")).suppress() +

        Concat(SkipTo(
            oneOf(genders) ^
            Word("|¶►") ^
            LineEnd()
        )).setResultsName("words") +

        Concat(Optional(OneOrMore(
            oneOf(genders) +
            Optional(Literal(" ")).suppress()
        ), default="UNKNOWN").setResultsName("gender")) +

        Optional((
            SkipTo(Literal("¶")).suppress() +
            Literal("¶").suppress() +
            Concat(SkipTo(Literal("►") ^ LineEnd()))
            # SkipTo(Word("►¶")).suppress()
        ).setResultsName("sources"), default="UNKNOWN")

    ) +

    Optional((
        SkipTo(Literal("►►")).suppress() +
        Literal("►►").suppress() +
        SkipTo(Literal("►") ^ LineEnd())
    ).setResultsName("misc"), default="UNKNOWN")
)

parsed = Concat(
    SkipTo(Word(alphas)).suppress() +
    (
        word_bold ^
        OneOrMore(Word(alphas))
    )
)

def schain(inp):
    return inp.replace('*', '').replace('\\', '').replace('/', '').strip()

def process_parsed(parsed):
    ldict = locals()
    exec("p_list = " + repr(parsed), globals(), ldict) #because pyparsing is stupid
    p_list = ldict['p_list']

    tmp_sources = []
    tmp_misc = []

    for source in p_list[1]['sources']:
        if source == "UNKNOWN":
            tmp_sources.append(source)
        elif source == "":
            tmp_sources.append("UNKNOWN")
        else:
            tmp_sources.append(source[0][0])

    p_list[1]['sources'] = tmp_sources

    for misc in p_list[1]['misc']:
        if misc == "UNKNOWN":
            tmp_misc.append(misc)
        else:
            tmp_misc.append(misc[0][0])

    if 'words' not in p_list[1].keys():
        p_list[1]['words'] = ["UNKNOWN"]

    p_list[1]['misc'] = tmp_misc

    # pp.pprint(p_list)
    # return

    return dict({
        'definition': schain(p_list[1]['definition'][0]),
        'words': [
            {'word': schain(a), 'source': schain(b), 'gender': schain(c)} for (a, b, c) in
            list(zip(p_list[1]['words'], p_list[1]['sources'], p_list[1]['gender']))
        ],
        'misc': schain(p_list[1]['misc'][0])
    })


def test(start, end):
    parsed_stuff = []
    for line in word_text[start:end]:
        try:
            parsed = word_def.parseString(line)
            parsed_stuff.append(process_parsed(parsed))
            # parsed_stuff.append(parsed)
        except KeyError as e:
            print(line)
            print(e.with_traceback())
        except:
            pass

    return parsed_stuff


def write(start, end):
    with open("../data/output.json", 'w') as output_json:
        json.dump(test(start, end), output_json)
