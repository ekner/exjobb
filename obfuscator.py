from itertools import takewhile
import re

inFile  = "4cbdbbb1bc6880ecff2f1bc6cb66444b319cc57cf47e8a35f956c36f5bec2bbb.wat"
outFile = "obfuscated.wat"

totLineWidth = 60

#i32_0 = "$obfuscator_i32_0"
#i32_1 = "$obfuscator_i32_1"
#i64_0 = "$obfuscator_i64_0"
#i64_1 = "$obfuscator_i64_1"

#i32_0 = "(;100;)"
#i32_1 = "(;101;)"
#i64_0 = "(;102;)"
#i64_1 = "(;103;)"

i32_0 = "20"
i32_1 = "21"
i64_0 = "22"
i64_1 = "23"

def copyIndentation(s):
    return "".join(list(takewhile(lambda x : x == ' ', s)))

def insertGlobals(lines):
    regexLst = ['^\s*\(type', '^\s*\(import', '^\s*\(table', '^\s*\(memory']
    largestLineNumber = 0
    for i in range(len(lines)):
        for elem in regexLst:
            if re.search(elem, lines[i]):
                largestLineNumber = i
    lines.insert(largestLineNumber + 1, f'(global (;{i32_0};) (mut i32) (i32.const 0))')
    lines.insert(largestLineNumber + 1, f'(global (;{i32_1};) (mut i32) (i32.const 0))')
    lines.insert(largestLineNumber + 1, f'(global (;{i64_0};) (mut i64) (i64.const 0))')
    lines.insert(largestLineNumber + 1, f'(global (;{i64_1};) (mut i64) (i64.const 0))')

def writeLines(f, lines, indent, comment):
    for line in lines:
        startLine = f"{indent}{line}"
        spaces = max(totLineWidth - len(startLine), 1) * ' '
        file.write(f"{startLine}{spaces};; {comment}\n")

###################################
#                                 #
#          Obfuscations:          #
#                                 #
###################################

obfOpaque = [
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
    ),
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
    ),
]

obfSub2 = [
    # i32
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
    # i64
    (
        "^\s*i64\.sub",
        [],
        False,
        [
            "i64.const -1",
            "i64.mul",
            "i64.add"
        ]
    ),
]

lines = []

with open(inFile) as file:
    lines = [line.rstrip() for line in file]

insertGlobals(lines)

with open(outFile, "w") as file:    
    for line in lines:
        obf = obfOpaque[0]
        #if re.search(obf[0], line) and not re.search("[\(\)]", line):
        if False:
            indent = copyIndentation(line)
            writeLines(file, obf[1], indent, 'obfuscated')
            writeLines(file, [line], '', 'original')
            writeLines(file, obf[3], indent, 'obfuscated')
        else:
            file.write(f"{line}\n")
