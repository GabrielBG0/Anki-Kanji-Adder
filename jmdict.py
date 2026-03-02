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
                self.index[r].append({"kanji": kanji, "glosses": glosses})

    def lookup(self, reading):
        """
        Lookup reading directly.
        Also supports suru-verb expansion.
        """

        # Direct match first
        if reading in self.index:
            return self.index[reading]

        results = []

        # Handle suru-verbs
        if reading.endswith("する"):
            base = reading[:-2]  # remove する

            if base in self.index:
                base_entries = self.index[base]

                for entry in base_entries:
                    # Reconstruct suru-kanji
                    new_entry = {
                        "kanji": (
                            [k + "する" for k in entry["kanji"]]
                            if entry["kanji"]
                            else []
                        ),
                        "glosses": entry["glosses"],
                    }
                    results.append(new_entry)

        return results
