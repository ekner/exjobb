from itertools import takewhile
import re
import functools
#import argparse

#parser=argparse.ArgumentParser()

#parser.add_argument("--input", help="Input file")
#parser.add_argument("--output", help="Output file")
#parser.add_argument("--obf", help="Obfuscation")

#args=parser.parse_args()

# Default values for arguments:
#IN_FILE = ""
#OUT_FILE = ""
#OBFUSCATION = ""

# Check supplied arguments and possible overwrite default ones:
#if args.input != None:
#    IN_FILE = args.input

#if args.output != None:
#    OUT_FILE = args.output
#else:
#    OUT_FILE = IN_FILE

#if args.obf != None:
#    OBFUSCATION = args.obf

totLineWidth = 60

i32_0 = "$obfuscator_i32_0"
i32_1 = "$obfuscator_i32_1"
i64_0 = "$obfuscator_i64_0"
i64_1 = "$obfuscator_i64_1"

#i32_0 = "(;100;)"
#i32_1 = "(;101;)"
#i64_0 = "(;102;)"
#i64_1 = "(;103;)"

#i32_0 = "120"
#i32_1 = "121"
#i64_0 = "122"
#i64_1 = "123"

def copyIndentation(s):
    return "".join(list(takewhile(lambda x : x == ' ', s)))

def insertGlobals(lines, statistics):
    regexLst = ['^\s*\(type', '^\s*\(import', '^\s*\(table', '^\s*\(memory', '^\s*\(global']
    largestLineNumber = 0
    for i in range(len(lines)):
        for elem in regexLst:
            if re.search(elem, lines[i]):
                largestLineNumber = i

    lastLine = False
    if (largestLineNumber == len(lines) - 1):
        lastLine = True
        lines[largestLineNumber] = lines[largestLineNumber][0:-1]

    lines.insert(largestLineNumber + 1, f'(global {i32_0} (mut i32) (i32.const 0))')
    lines.insert(largestLineNumber + 1, f'(global {i32_1} (mut i32) (i32.const 0))')
    lines.insert(largestLineNumber + 1, f'(global {i64_0} (mut i64) (i64.const 0))')
    lines.insert(largestLineNumber + 1, f'(global {i64_1} (mut i64) (i64.const 0))')

    statistics["linesAdded"] += 4

    if (lastLine):
        lines.append(")")
        statistics["linesAdded"] += 1

def writeLines(file, lines, indent, comment):
    for line in lines:
        startLine = f"{indent}{line}"
        spaces = max(totLineWidth - len(startLine), 1) * ' '
        file.write(f"{startLine}{spaces};; {comment}\n")

###################################
#                                 #
#          Obfuscations:          #
#                                 #
###################################

obfOpaque1 = [
    # Saker som tar i32 som parameter och returnerar i32:
    (
        "^\s*i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s)",
        [
            f"global.set {i32_0}",
            f"global.set {i32_1}",
            "i32.const 1",
            "if (result i32)",
            f"global.get {i32_1}",
            f"global.get {i32_0}",
        ],
        True,
        [
            "else",
            "i32.const 42",
            "end"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i32:
    (
        "^\s*i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s)",
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            "i32.const 1",
            "if (result i32)",
            f"global.get {i64_1}",
            f"global.get {i64_0}",
        ],
        True,
        [
            "else",
            "i32.const 42",
            "end"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            "i32.const 1",
            "if (result i64)",
            f"global.get {i64_1}",
            f"global.get {i64_0}",
        ],
        True,
        [
            "else",
            "i64.const 42",
            "end"
        ]
    )
]

obfOpaque2 = [
    # Saker som tar i32 som parameter och returnerar i32:
    (
        "^\s*i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s)",
        [
            f"global.set {i32_0}",
            f"global.set {i32_1}",
            "i32.const 1",
            "i32.const 1",
            "i32.eq",
            "if (result i32)",
            f"global.get {i32_1}",
            f"global.get {i32_0}",
        ],
        True,
        [
            "else",
            "i32.const 42",
            "end"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i32:
    (
        "^\s*i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s)",
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            "i32.const 1",
            "i32.const 1",
            "i32.eq",
            "if (result i32)",
            f"global.get {i64_1}",
            f"global.get {i64_0}",
        ],
        True,
        [
            "else",
            "i32.const 42",
            "end"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            "i32.const 1",
            "i32.const 1",
            "i32.eq",
            "if (result i64)",
            f"global.get {i64_1}",
            f"global.get {i64_0}",
        ],
        True,
        [
            "else",
            "i64.const 42",
            "end"
        ]
    )
]

obfOpaque3 = [
    # Saker som tar i32 som parameter och returnerar i32:
    (
        "^\s*i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s)",
        [
            f"global.set {i32_0}",
            f"global.set {i32_1}",
            "i32.const 1",
            "i32.const 2",
            "i32.add",
            "i32.const 3",
            "i32.eq",
            "if (result i32)",
            f"global.get {i32_1}",
            f"global.get {i32_0}",
        ],
        True,
        [
            "else",
            "i32.const 42",
            "end"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i32:
    (
        "^\s*i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s)",
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            "i32.const 1",
            "i32.const 2",
            "i32.add",
            "i32.const 3",
            "i32.eq",
            "if (result i32)",
            f"global.get {i64_1}",
            f"global.get {i64_0}",
        ],
        True,
        [
            "else",
            "i32.const 42",
            "end"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            "i32.const 1",
            "i32.const 2",
            "i32.add",
            "i32.const 3",
            "i32.eq",
            "if (result i64)",
            f"global.get {i64_1}",
            f"global.get {i64_0}",
        ],
        True,
        [
            "else",
            "i64.const 42",
            "end"
        ]
    )
]

obfDead1 = [
    # Saker som tar i32 eller i64 som parameter och returnerar i32:
    (
        "^\s*(i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))|(i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))",
        [],
        True,
        [
            "i32.const 0",
            "i32.add"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [],
        True,
        [
            "i64.const 0",
            "i64.add"
        ]
    )
]

obfDead2 = [
    # Saker som tar i32 eller i64 som parameter och returnerar i32:
    (
        "^\s*(i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))|(i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))",
        [],
        True,
        [
            "i32.const 1",
            "i32.mul"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [],
        True,
        [
            "i64.const 1",
            "i64.mul"
        ]
    )
]

obfDead3 = [
    # Saker som tar i32 eller i64 som parameter och returnerar i32:
    (
        "^\s*(i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))|(i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))",
        [],
        True,
        [
            "i32.const -1",
            "i32.and"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [],
        True,
        [
            "i64.const -1",
            "i64.and"
        ]
    )
]

obfDead4 = [
    # Saker som tar i32 eller i64 som parameter och returnerar i32:
    (
        "^\s*(i32\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr|eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))|(i64\.(eq[^z]|ne|lt_u|lt_s|gt_u|gt_s|le_u|le_s|ge_u|ge_s))",
        [],
        True,
        [
            "i32.const 0",
            "i32.or"
        ]
    ),
    # Saker som tar i64 som parameter och returnerar i64:
    (
        "^\s*i64\.(add|sub|mul|div_u|div_s|rem_u|rem_s|and|or|xor|shl|shr_u|shr_s|rotl|rotr)",
        [],
        True,
        [
            "i64.const 0",
            "i64.or"
        ]
    )
]

obfSub1 = [
    # i32 add
    (
        "^\s*i32\.add",
        [],
        False,
        [
            "i32.const -1",
            "i32.mul",
            "i32.sub"
        ]
    ),
    # i64 add
    (
        "^\s*i64\.add",
        [],
        False,
        [
            "i64.const -1",
            "i64.mul",
            "i64.sub"
        ]
    )
]

obfSub2 = [
    # i32 sub
    (
        "^\s*i32\.sub",
        [],
        False,
        [
            "i32.const -1",
            "i32.mul",
            "i32.add"
        ]
    ),
    # i64 sub
    (
        "^\s*i64\.sub",
        [],
        False,
        [
            "i64.const -1",
            "i64.mul",
            "i64.add"
        ]
    )
]

obfSub3 = [
    # i32
    (
        "^\s*i32\.and",
        [],
        False,
        [
            f"global.set {i32_0}",
            "i32.const -1",
            "i32.xor",
            f"global.get {i32_0}",
            "i32.xor",
            f"global.get {i32_0}",
            "i32.and"
        ]
    ),
    # i64
    (
        "^\s*i64\.and",
        [],
        False,
        [
            f"global.set {i64_0}",
            "i64.const -1",
            "i64.xor",
            f"global.get {i64_0}",
            "i64.xor",
            f"global.get {i64_0}",
            "i64.and"
        ]
    )
]

obfSub4 = [
    # i32
    (
        "^\s*i32\.or",
        [],
        False,
        [
            f"global.set {i32_0}",
            f"global.set {i32_1}",
            f"global.get {i32_0}",
            f"global.get {i32_1}",
            "i32.xor",
            f"global.get {i32_0}",
            f"global.get {i32_1}",
            "i32.and",
            "i32.or"
        ]
    ),
    # i64
    (
        "^\s*i64\.or",
        [],
        False,
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            f"global.get {i64_0}",
            f"global.get {i64_1}",
            "i64.xor",
            f"global.get {i64_0}",
            f"global.get {i64_1}",
            "i64.and",
            "i64.or"
        ]
    )
]

obfSub5 = [
    # i32
    (
        "^\s*i32\.xor",
        [],
        False,
        [
            f"global.set {i32_0}",
            f"global.set {i32_1}",
            f"global.get {i32_0}",
            "i32.const -1",
            "i32.xor",
            f"global.get {i32_1}",
            "i32.and",
            f"global.get {i32_1}",
            "i32.const -1",
            "i32.xor",
            f"global.get {i32_0}",
            "i32.and",
            "i32.or"
        ]
    ),
    # i64
    (
        "^\s*i64\.xor",
        [],
        False,
        [
            f"global.set {i64_0}",
            f"global.set {i64_1}",
            f"global.get {i64_0}",
            "i64.const -1",
            "i64.xor",
            f"global.get {i64_1}",
            "i64.and",
            f"global.get {i64_1}",
            "i64.const -1",
            "i64.xor",
            f"global.get {i64_0}",
            "i64.and",
            "i64.or"
        ]
    ),
]

subMap = {
    "d1": obfDead1,
    "d2": obfDead2,
    "d3": obfDead3,
    "d4": obfDead4,
    "o1": obfOpaque1,
    "o2": obfOpaque2,
    "o3": obfOpaque3,
    "s1": obfSub1,
    "s2": obfSub2,
    "s3": obfSub3,
    "s4": obfSub4,
    "s5": obfSub5
}

def strToObf(s):
    obfType = s[0]
    numbers = s[1:]
    return list(functools.reduce(lambda acc, x: acc + subMap[obfType + x], numbers, []))

# Perform obfuscation for a certain LINE in a file:
def performObfuscation(line, file, obfuscation, statistics):
    replacementFound = False
    obfuscations = strToObf(obfuscation)

    for obf in obfuscations:
        if re.search(obf[0], line) and not re.search("[\(\)]", line):
            replacementFound = True
            statistics["matches"] += 1
            indent = copyIndentation(line)
            writeLines(file, obf[1], indent, 'obfuscated')
            if obf[2]:
                writeLines(file, [line], '', 'original')
            else:
                statistics["linesRemoved"] += 1
            writeLines(file, obf[3], indent, 'obfuscated')
            statistics["linesAdded"] += len(obf[1]) + len(obf[3])
            break
    if not replacementFound:
        file.write(f"{line}\n")  

# Perform obfuscation/s for a whole file:
def obfuscateFile(inOutFile, obfuscations):
    statistics = {
        "linesRemoved": 0,
        "linesAdded": 0,
        "linesBefore": None,
        "matches": 0
    }

    for obfuscation in obfuscations:
        lines = []
    
        with open(inOutFile) as file:
            lines = [line.rstrip() for line in file]

        statistics["linesBefore"] = len(lines)
        insertGlobals(lines, statistics)

        with open(inOutFile, "w") as file:
            for line in lines:
                performObfuscation(line, file, obfuscation, statistics)
    
    return statistics
