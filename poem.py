import translation
import random

structures = [
        (("noun", "verb", "noun"), (2, 1, 0)),
        (("noun", "adjective"), (0, 1))
        ]


class Poem(object):
    def __init__(self, lines=3):
        while True:
            self.sentences = []
            self.structures = []
            self.words = []
            while len(self.words) < lines * 3:
                struct = random.choice(structures)
                forms, _ = struct
                sent = [translation.langword(form) for form in forms]
                self.sentences.append(sent)
                self.structures.append(struct)
                self.words.extend(sent)
            if len(self.words) % 3 == 0:
                break
        self.lines = []
        for i in range(len(self.words) // 3):
            self.lines.append(self.words[3 * i:3 * i + 3])

    def gloss(self):
        gloss = []
        for struct, sent in zip(self.structures, self.sentences):
            forms, idxs = struct
            for idx in idxs:
                words = translation.translate(sent[idx])
                if words:
                    gloss.append(words[0])
                elif not gloss or gloss[-1] is not None:
                    gloss.append(None)
            gloss.append("/")
        return gloss[:-1]
