CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k",
               "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y",
               "", "e", "yu", "ja", "je", "i", "ji", "g")

TRANS = {}

for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()



def normalize(name):
    global TRANS
    normalized = ''
    nums = '1234567890'
    for i in name:
        if i.isalpha() == False and i not in nums and not ".":
            i = '_'
            normalized += i
        else:
            normalized += i
    return normalized.translate(TRANS)