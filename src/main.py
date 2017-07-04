from pyparsing import Optional, Literal, OneOrMore, oneOf, alphanums, Or, Word, alphas8bit, nums, printables, SkipTo, LineStart, ZeroOrMore, LineEnd, Group, NotAny
import pprint as pp
import sys
import re
import unicodedata
import json
# import pyparsing as pp

alphas = alphanums + alphas8bit
genders = "m. n. f. pl. m.pl. n.pl. f.pl. indecl."


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


#TODO: make sources optional

word_def = (
    LineStart() +
    Optional(Word(nums + " /")).suppress() +
    Concat(SkipTo(Word("►¶"))).setResultsName("definition") +
    OneOrMore(
        Literal("►").suppress() +
        NotAny(Literal("►")).suppress() +

        Concat(SkipTo(
            oneOf(genders) ^
            Word("|.¶")
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
        SkipTo(LineEnd())
    ).setResultsName("notes"), default="UNKNOWN")
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
    tmp_notes = []

    for source in p_list[1]['sources']:
        if source == "UNKNOWN":
            tmp_sources.append(source)
        else:
            tmp_sources.append(source[0][0])

    p_list[1]['sources'] = tmp_sources

    for note in p_list[1]['notes']:
        if note == "UNKNOWN":
            tmp_notes.append(note)
        else:
            tmp_notes.append(note[0][0])

    p_list[1]['notes'] = tmp_notes

    # pp.pprint(p_list)
    # return

    return dict({
        'definition': schain(p_list[1]['definition'][0]),
        'words': [
            {'word': schain(a), 'source': schain(b), 'gender': schain(c)} for (a, b, c) in
            list(zip(p_list[1]['words'], p_list[1]['sources'], p_list[1]['gender']))
        ],
        'notes': schain(p_list[1]['notes'][0])
    })


def test(start, end):
    parsed_stuff = []
    for line in word_text[start:end]:
        try:
            parsed = word_def.parseString(line)
            parsed_stuff.append(process_parsed(parsed))
            # parsed_stuff.append(parsed)
        except KeyError as e:
            print(e)
        except:
            pass

    return parsed_stuff


def write(start, end):
    with open("../data/output.json", 'w') as output_json:
        json.dump(test(start, end), output_json)
