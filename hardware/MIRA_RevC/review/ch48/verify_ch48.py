"""Validate exported KiCad XML netlists against the CH48 interface contract.

Usage: python3 verify_ch48.py CONTROL.xml MODULE.xml
"""
import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


class Netlist:
    def __init__(self, xml, reference_map=None):
        tree = ET.parse(xml)
        # Normalize the page-based annotation back to the CH48 contract names.
        aliases = {new: old for old, new in (reference_map or {}).items()}
        for item in tree.findall("components/comp") + tree.findall("nets/net/node"):
            ref = item.get("ref")
            item.set("ref", aliases.get(ref, ref))
        self.values = {c.attrib["ref"]: c.findtext("value") for c in tree.findall("components/comp")}
        # KiCad 10 may qualify node pinfunction with _<pin number>.
        # Resolve through libparts, accepting only the exact matching spelling.
        definitions = {
            (part.get("lib"), part.get("part"), pin.get("num")): pin.get("name", "")
            for part in tree.findall("libparts/libpart")
            for pin in part.findall("pins/pin")
        }
        sources = {
            comp.get("ref"): (comp.find("libsource").get("lib"),
                              comp.find("libsource").get("part"))
            for comp in tree.findall("components/comp")
        }
        self.pins = {}
        self.by_net = {}
        for net in tree.findall("nets/net"):
            name = net.attrib["name"]
            # Local channel labels may move between sheets during drawing cleanup.
            # Normalize only contract-specific CH0..CH47 names, rejecting duplicate
            # scoped aliases rather than silently joining independent electrical nets.
            local = name.rsplit("/", 1)[-1]
            if name.startswith("/") and re.fullmatch(r"CH(?:[0-9]|[1-3][0-9]|4[0-7])_[A-Za-z0-9_]+", local):
                name = local
            if name in self.by_net:
                raise ValueError(f"Ambiguous channel net after local-name normalization: {name}")
            nodes = self.by_net[name] = []
            for node in net.findall("node"):
                key = (node.attrib["ref"], node.attrib["pin"])
                if key in self.pins:
                    raise ValueError(f"{key} appears twice")
                self.pins[key] = name
                function = node.get("pinfunction", "")
                canonical = definitions[(*sources[key[0]], key[1])]
                accepted = (canonical, canonical + "_" + key[1])
                if canonical == "~":
                    accepted += ("",)
                if function not in accepted:
                    raise ValueError(f"{key}: unexpected pinfunction {function}")
                nodes.append((key[0], key[1], canonical))

    def pin(self, ref, pin):
        return self.pins[ref, str(pin)]

    def expect(self, ref, pin, expected):
        actual = self.pin(ref, pin)
        if actual != expected:
            raise ValueError(f"{ref}.{pin} is {actual}, expected {expected}")

    def expect_part(self, net, value, pin_function):
        if not any(self.values[r] == value and name == pin_function
                   for r, _, name in self.by_net[net]):
            raise ValueError(f"{net}: missing {value} {pin_function}")


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("control")
    arg.add_argument("module")
    arg.add_argument("--reference-map", type=Path,
                     help="JSON map from original to page-based references")
    args = arg.parse_args()
    maps = json.loads(args.reference_map.read_text()) if args.reference_map else {}
    ctrl = Netlist(args.control, maps.get("MIRA_Control"))
    mod = Netlist(args.module, maps.get("MIRA_Crossbar"))
    counts = Counter(ctrl.values.values())
    expected = {"DAC81416": 3, "AD4696BCPZ": 6, "INA821IDR": 48, "MAX313EUE+": 12,
                "OPA4323IPWR": 24, "TMUX7208": 18, "TMUX6112": 36, "OPA192IDR": 12}
    if any(counts[part] != total for part, total in expected.items()):
        raise ValueError("Converter / front-end part count differs from CH48 design")
    # Explicitly compare all 80 ordinary positions plus the four Hirose power contacts.
    for cr, mr in [("J1800", "J1"), ("J1801", "J2")]:
        for pin in list(range(1, 81)) + ["P1", "P2", "P3", "P4"]:
            a, b = ctrl.pin(cr, pin), mod.pin(mr, pin)
            if a != b and not (a.startswith("unconnected-") and b.startswith("unconnected-")):
                raise ValueError(f"{cr}/{mr} pad {pin}: {a} != {b}")
            if str(pin).startswith("P"):
                ctrl.expect(cr, pin, "GND")
    rows = list(csv.DictReader(Path(__file__).with_name("socket-map.csv").open(encoding="utf-8")))
    if [int(row["socket_pin"]) for row in rows] != list(range(1, 65)):
        raise ValueError("Incomplete socket map")
    for row in rows:
        pin, target = row["socket_pin"], row["net"]
        if target == "NC":
            if not mod.pin("U1", pin).startswith("unconnected-"):
                raise ValueError(f"U1.{pin} should be NC")
        else:
            mod.expect("U1", pin, target)
    for ref, net in [("R1", "CASE"), ("R2", "GND_REF")]:
        mod.expect(ref, 1, net)
        mod.expect(ref, 2, "GND")
    for i in range(48):
        h = f"CH{i}"
        bank, ch = divmod(i, 16)
        quartet, slot = divmod(i, 4)
        t = 10000 + 20*i
        cr, mr = ("J1800", "J1") if i < 32 else ("J1801", "J2")
        index = i if i < 32 else i-32
        pin = 1 + index + index//2
        ctrl.expect(cr, pin, h)
        mod.expect(mr, pin, h)
        nodes = mod.by_net[h]
        if len(nodes) != 2 or not any(ref == "U1" for ref, _, _ in nodes):
            raise ValueError(f"Unexpected endpoints on module {h}")
        ctrl.expect_part(h+"_SET", "DAC81416", "OUT"+str(ch))
        for offset, suffix in enumerate(["_VADC", "_IADC"]):
            adc = f"U{2000+2*bank+offset}"
            matches = [ref for ref, _, func in ctrl.by_net[h+suffix] if func == "IN"+str(ch)]
            if matches != [adc]:
                raise ValueError(f"{h}{suffix}: wrong ADC input")
        for pin_no, net in enumerate([h+"_S_MINUS", h+"_RG1", h+"_RG2", h+"_DRV", "N15", "MID2V048", h+"_IRAW", "P15"], 1):
            ctrl.expect(f"U{t}", pin_no, net)
        ctrl.expect_part(h, "MAX313EUE+", "COM"+str(slot+1))
        ctrl.expect_part(h+"_S_MINUS", "MAX313EUE+", "NO"+str(slot+1))
        ctrl.expect_part(h+"_EN", "MAX313EUE+", "IN"+str(slot+1))
        ctrl.expect_part(h+"_EN", "TMUX6112", "SEL"+str(slot+1))
        ctrl.expect_part(h+"_SET", "OPA4192", "IN"+"ABCD"[slot]+"+")
        for role in range(3):
            mux=f"U{15101+10*role+i//8}"
            ctrl.expect(mux, [4,5,6,7,12,11,10,9][i%8], h+"_SERVICE")
            ctrl.expect(mux, 8, ["BL_FORM_BUS","NL_FORM_BUS","FORM_GATE_SERIES"][role])
        isolate=f"U{15300+quartet}"
        ctrl.expect(isolate, [3,14,11,6][slot], h)
        ctrl.expect(isolate, [2,15,10,7][slot], h+"_SERVICE")
        ctrl.expect(isolate, [1,16,9,8][slot], "FORM_GATE_VALID")
        ctrl.expect(f"R{t+6}",1,h)
        ctrl.expect(f"R{t+6}",2,h+"_BLEED_R")
        ctrl.expect(f"U{13002+10*quartet}", [1,16,9,8][slot], "CH_BLEED_EN")
    for ref, value in ctrl.values.items():
        if value == "MAX313EUE+":
            ctrl.expect(ref,12,"ANA5")
    for ref in ("C300","C301"):
        ctrl.expect(ref,1,"SYS3V3")
    print("PASS: 48 electrode nets, 96 ADC inputs, 48 DAC outputs, 144 forming taps, "
          "48 bleed controls, 168 mating positions and 64 socket pins.")


if __name__ == "__main__":
    main()
