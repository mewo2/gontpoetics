import spacy
import numpy as np
import inflect
import language

np.random.seed(0)

lang = language.Language(
    phonemes={'V': 'AEIOU',
              'C': 'PTKMSL'}, syll='CV', wordlength=(3, 6))


nlp = spacy.load('en', tagger=False, parser=False, entity=False, matcher=False)


def load_words(filename):
    return [nlp(w) for w in open(filename).read().split("\n") if w.strip()]


nouns = load_words("nouns.txt")
verbs = load_words("verbs.txt")
adjectives = load_words("adjectives.txt")

for word in nouns + verbs + adjectives:
    assert word.vector.sum() != 0.0, word
def cosine(u, v):
    return np.dot(u, v) / (np.dot(u, u) * np.dot(v, v))**0.5


def randomsense():
    return np.random.randn(300)


def bestvector(w):
    return max(w, key=len).vector


def getword(sense, form, cutoff=0.13):
    words = {"noun": nouns, "verb": verbs, "adjective": adjectives}[form]
    p = np.array([cosine(bestvector(w), sense) for w in words])
    if p.max() < cutoff:
        return []
    p[p < cutoff] = -1000
    p -= p.max()
    p = np.exp(20 * p)
    p /= p.sum()
    words = [w.text for w in words]

    allmeanings = [(p_, w) for p_, w in sorted(
        zip(p, words), reverse=True) if p_ > 1e-3]

    meanings = []
    totalp = 0
    for p_, w in allmeanings:
        meanings.append(w)
        totalp += p_
        if len(meanings) > 1 or totalp > 0.5:
            break
    return meanings


lexicon = {}

def langword(form):
    word = lang.word(form)
    if word not in lexicon:
        lexicon[word] = randomsense(), form
    return word

inflect = inflect.engine()


def infinitive(verb):
    if verb.startswith("is "):
        return "be " + verb[3:]
    else:
        words = verb.split()
        words[0] = inflect.plural_verb(words[0])
        return ' '.join(words)


def strip_a(noun):
    if noun.startswith('a '):
        return noun[2:]
    if noun.startswith('an '):
        return noun[3:]
    return noun


def translate(word):
    ws = getword(*lexicon[word])
    _, form = lexicon[word]
    if form == 'adjective':
        ws = ["is " + w for w in ws]
    return ws

def gloss(word):
    ws = translate(word)
    _, form = lexicon[word]
    if form == 'verb':
        ws = ["to " + infinitive(w) for w in ws]
    if form == 'noun':
        ws = [strip_a(w) for w in ws]
    if form == 'adjective':
        ws = [w[3:] for w in ws]
    return ws
