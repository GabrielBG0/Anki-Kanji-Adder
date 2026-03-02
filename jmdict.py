import xml.etree.ElementTree as ET

class JMDict:
    def __init__(self, path):
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()
        self.index = {}
        self._build_index()

    def _build_index(self):
        for entry in self.root.findall("entry"):
            readings = [r.find("reb").text for r in entry.findall("r_ele")]
            kanji = [k.find("keb").text for k in entry.findall("k_ele")]
            glosses = []

            for sense in entry.findall("sense"):
                glosses += [g.text.lower() for g in sense.findall("gloss")]

            for r in readings:
                if r not in self.index:
                    self.index[r] = []
                self.index[r].append({
                    "kanji": kanji,
                    "glosses": glosses
                })

    def lookup(self, reading):
        return self.index.get(reading, [])