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
        Supports light-verb and auxiliary constructions.
        """

        # 1. Direct match
        if reading in self.index:
            return self.index[reading]

        results = []

        # Expand using known patterns
        expansions = self._expand_reading(reading)

        for base_reading, suffix_builder in expansions:
            if base_reading in self.index:
                base_entries = self.index[base_reading]

                for entry in base_entries:
                    kanji_list = entry["kanji"]

                    if not kanji_list:
                        continue

                    new_entry = {
                        "kanji": [suffix_builder(k) for k in kanji_list],
                        "glosses": entry["glosses"],
                    }

                    results.append(new_entry)

        return results

    def _expand_reading(self, reading):
        """
        Returns list of (base_reading, kanji_builder_function)
        """

        expansions = []

        # する verbs
        if reading.endswith("する"):
            base = reading[:-2]
            expansions.append((base, lambda k: k + "する"))

        # がある
        if reading.endswith("がある"):
            base = reading[:-3]
            expansions.append((base, lambda k: k + "がある"))

        # がない
        if reading.endswith("がない"):
            base = reading[:-3]
            expansions.append((base, lambda k: k + "がない"))

        # をする
        if reading.endswith("をする"):
            base = reading[:-3]
            expansions.append((base, lambda k: k + "をする"))

        # になる
        if reading.endswith("になる"):
            base = reading[:-3]
            expansions.append((base, lambda k: k + "になる"))

        return expansions
