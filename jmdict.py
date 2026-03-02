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
            pos_tags = set()

            for sense in entry.findall("sense"):
                glosses += [g.text.lower() for g in sense.findall("gloss")]

                for pos in sense.findall("pos"):
                    pos_tags.add(pos.text)

            for r in readings:
                if r not in self.index:
                    self.index[r] = []

                self.index[r].append(
                    {
                        "kanji": kanji,
                        "glosses": glosses,
                        "pos": pos_tags,
                    }
                )

    def lookup(self, reading):
        """
        Lookup reading directly.
        Supports POS-aware light constructions.
        """

        # Direct match
        if reading in self.index:
            return self.index[reading]

        results = []
        expansions = self._expand_reading(reading)

        for base_reading, builder, pos_filter in expansions:
            if base_reading not in self.index:
                continue

            for entry in self.index[base_reading]:
                if not pos_filter(entry):
                    continue

                if not entry["kanji"]:
                    continue

                results.append(
                    {
                        "kanji": [builder(k) for k in entry["kanji"]],
                        "glosses": entry["glosses"],
                        "pos": entry["pos"],
                    }
                )

        return results

    def _expand_reading(self, reading):
        """
        Returns list of (base_reading, builder, pos_filter)
        pos_filter is a function(entry) -> bool
        """

        expansions = []

        # --- する verbs ---
        if reading.endswith("する"):
            base = reading[:-2]

            def allow_suru(entry):
                # Allow if entry is marked as suru-verb OR noun
                pos = entry["pos"]
                return any("vs" in p.lower() for p in pos) or any(
                    "noun" in p.lower() for p in pos
                )

            expansions.append((base, lambda k: k + "する", allow_suru))

        # --- がある ---
        if reading.endswith("がある"):
            base = reading[:-3]

            def allow_noun(entry):
                pos = entry["pos"]
                return any("noun" in p.lower() for p in pos)

            expansions.append((base, lambda k: k + "がある", allow_noun))

        # --- がない ---
        if reading.endswith("がない"):
            base = reading[:-3]

            def allow_noun(entry):
                pos = entry["pos"]
                return any("noun" in p.lower() for p in pos)

            expansions.append((base, lambda k: k + "がない", allow_noun))

        # --- をする ---
        if reading.endswith("をする"):
            base = reading[:-3]

            def allow_noun(entry):
                pos = entry["pos"]
                return any("noun" in p.lower() for p in pos)

            expansions.append((base, lambda k: k + "をする", allow_noun))

        # --- になる ---
        if reading.endswith("になる"):
            base = reading[:-3]

            def allow_adj_or_noun(entry):
                pos = entry["pos"]
                return any("adj" in p.lower() for p in pos) or any(
                    "noun" in p.lower() for p in pos
                )

            expansions.append((base, lambda k: k + "になる", allow_adj_or_noun))

        return expansions
