"""Check saved RevC boards and the 90 Final-Control pad pairs with pcbnew."""
import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path

import pcbnew as k

ROOT = Path(__file__).resolve().parents[3]
LAYOUT = ROOT / "review/layout"


def xy(pos):
    return tuple(k.ToMM(c) for c in (pos.x, pos.y))


def uid(item):
    return item.m_Uuid.AsString()


def footprint_map(board):
    return {f.GetReference(): f for f in board.GetFootprints()}


def pad_map(board):
    return {(f.GetReference(), p.GetNumber()): p
            for f in board.GetFootprints() for p in f.Pads() if p.GetNumber()}


def outline(board):
    shape = k.SHAPE_POLY_SET()
    assert board.GetBoardPolygonOutlines(shape, False)
    assert shape.OutlineCount() == 1
    ring = shape.COutline(0)
    return sorted(xy(ring.CPoint(i)) for i in range(ring.PointCount()))


def electric_identity(board):
    return {uid(f): (f.GetReference(), f.GetValue(), (str(f.GetFPID().GetLibNickname()), str(f.GetFPID().GetLibItemName())),
                     str(f.GetPath().AsString()), f.GetLayer(),
                     sorted((uid(p), p.GetNumber(), p.GetNetname(), p.GetLayerSet().FmtBin())
                            for p in f.Pads()))
            for f in board.GetFootprints()}


def compare_pairs(boards):
    footprints = {name: footprint_map(board) for name, board in boards.items()}
    pads = {name: pad_map(board) for name, board in boards.items()}
    expected = {p["pair"]: p["pins"] for p in json.loads(
        (LAYOUT / "MIRA-01.01.00/pair-pin-checks.json").read_text())}
    pin_count = 0
    data = []
    with (LAYOUT / "connector-map.csv").open() as file:
        for row in csv.DictReader(file):
            name = row["pair"]
            cb, mb = "Control", row["mate_board"].removeprefix("MIRA_")
            cr, mr = row["control_ref"], row["mate_ref"]
            control, mate = footprints[cb][cr], footprints[mb][mr]
            origin = xy(control.GetPosition())
            assert origin == xy(mate.GetPosition())
            assert control.IsFlipped() == (mb == "Power") and mate.IsFlipped() == (mb == "Crossbar")
            assert math.isclose(control.GetOrientationDegrees() % 360, float(row["control_angle"]) % 360)
            assert math.isclose(mate.GetOrientationDegrees() % 360, float(row["mate_angle"]) % 360)
            pins = expected[name]
            assert {n for r, n in pads[cb] if r == cr} == {p["pin"] for p in pins}
            assert {n for r, n in pads[mb] if r == mr} == {p["pin"] for p in pins}
            for p in pins:
                cp, mp = pads[cb][(cr, p["pin"])], pads[mb][(mr, p["pin"])]
                assert (cp.GetNetname(), mp.GetNetname()) == (p["control_net"], p["mate_net"]), (name, p)
                measured = [b - a for a, b in zip(xy(cp.GetPosition()), xy(mp.GetPosition()))]
                assert all(math.isclose(a, b, abs_tol=0.000001) for a, b in zip(measured, p["pad_delta_mm"]))
                pin_count += 1
            data.append(dict(pair=name, control=cr, mate=mr, xy=origin,
                             pins=len(pins), gap=int(row["gap_mm"]),
                             pin1_control=xy(pads[cb][(cr, "1")].GetPosition()),
                             pin1_mate=xy(pads[mb][(mr, "1")].GetPosition())))
    assert len(data) == 10
    return dict(count=pin_count, pairs=data)


def support_axes(boards):
    parts = {name: footprint_map(board) for name, board in boards.items()}
    support = {}
    for ref in ("H9101", "H9102", "H9103", "H9104", "H9301", "H9302"):
        a, b = (parts[label][ref] for label in ("Control", "Power"))
        assert xy(a.GetPosition()) == xy(b.GetPosition())
        assert xy(next(iter(a.Pads())).GetDrillSize()) == (3.2, 3.2)
        assert xy(next(iter(b.Pads())).GetDrillSize()) == (3.2, 3.2)
        support[ref] = xy(a.GetPosition())
    assert xy(parts["Control"]["H1802"].GetPosition()) == xy(parts["Crossbar"]["H3"].GetPosition())
    assert parts["Power"]["U1101"].IsFlipped() and parts["Power"]["J301"].IsFlipped()
    return support


def routes(board):
    return sorted((t.GetNetname(), xy(t.GetStart()), xy(t.GetEnd()),
                   board.GetLayerName(t.GetLayer()), k.ToMM(t.GetWidth(t.TopLayer()) if isinstance(t, k.PCB_VIA) else t.GetWidth()),
                   t.GetViaType() if isinstance(t, k.PCB_VIA) else None,
                   k.ToMM(t.GetDrillValue()) if isinstance(t, k.PCB_VIA) else None,
                   t.BottomLayer() if isinstance(t, k.PCB_VIA) else None)
                  for t in board.GetTracks())


def reference_planes(board):
    """Count sampled track centreline points above or below filled GND."""
    signals = {k.F_Cu: k.In2_Cu, k.In1_Cu: k.In2_Cu, k.In3_Cu: k.In2_Cu,
               k.In5_Cu: k.In6_Cu, k.B_Cu: k.In6_Cu}
    fill = {layer: [z.GetFilledPolysList(layer) for z in board.Zones()
                    if z.GetNetname() == "GND" and z.IsOnLayer(layer)]
            for layer in set(signals.values())}
    counts = {}
    for t in board.GetTracks():
        if isinstance(t, k.PCB_VIA):
            continue
        layer = t.GetLayer()
        if layer not in signals:
            continue
        n = t.GetNetname().rsplit("/", 1)[-1]
        if not n.startswith(("PS_DDR_", "FX_USB3RX1", "CH0")) and n not in ("CH30", "CH31"):
            continue
        start, end = t.GetStart(), t.GetEnd()
        intervals = max(1, math.ceil(math.dist(xy(start), xy(end)) / .25))
        key = f"{n} | {board.GetLayerName(layer)} | {board.GetLayerName(signals[layer])}"
        row = counts.setdefault(key, [0, 0])
        for i in range(intervals):
            fraction = (i + .5) / intervals
            sample = k.VECTOR2I(round(start.x + fraction * (end.x - start.x)),
                                round(start.y + fraction * (end.y - start.y)))
            row[0] += 1
            row[1] += any(poly.Contains(sample) for poly in fill[signals[layer]])
    return counts


def verify_trial(board):
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    conn.RecalculateRatsnest()
    pads = pad_map(board)
    count = 0
    with (LAYOUT / "acceptance-01.03-01.04/connectivity.csv").open() as file:
        for row in csv.DictReader(file):
            if row["trial"] != "hdi":
                continue
            a, b = (pads[tuple(row[key].split("."))] for key in ("start", "end"))
            assert a.GetNetname() == b.GetNetname() == row["net"], row
            assert uid(b) in {uid(item) for item in conn.GetConnectedItems(a)}, row
            count += 1
    assert count == 90
    return count


def edge_occupancy(board, bounds):
    edges = {f"{side}_{edge}": (float("inf"), "") for side in ("F", "B")
             for edge in ("west", "north", "east", "south")}
    for f in board.GetFootprints():
        rect = f.GetCourtyard(k.B_CrtYd if f.IsFlipped() else k.F_CrtYd)
        rect = rect.BBox() if rect.OutlineCount() else f.GetBoundingBox(False, False)
        x0, y0 = xy(rect.GetOrigin())
        x1, y1 = xy(rect.GetEnd())
        side = "B" if f.IsFlipped() else "F"
        for edge, gap in zip(("west", "north", "east", "south"),
                             (x0-bounds[0], y0-bounds[1], bounds[2]-x1, bounds[3]-y1)):
            key = f"{side}_{edge}"
            edges[key] = min(edges[key], (round(gap, 3), f.GetReference()))
    return edges


def load(paths):
    return {name: k.LoadBoard(str(path)) for name, path in zip(
        ("Control", "Power", "Crossbar", "Final"), paths, strict=True)}


def measure(boards):
    result = {}
    for name, board in boards.items():
        corners = outline(board)
        bounds = (*map(min, zip(*corners)), *map(max, zip(*corners)))
        conn = board.GetConnectivity()
        board.BuildConnectivity()
        conn.RecalculateRatsnest()
        types = Counter(str(t.GetViaType()) for t in board.GetTracks() if isinstance(t, k.PCB_VIA))
        result[name] = dict(corners=corners, bounds=bounds, footprints=len(board.GetFootprints()),
                            edge_courtyard_mm=edge_occupancy(board, bounds),
                            via_types=dict(types), ratsnest=conn.GetUnconnectedCount(False))
    assert result["Control"]["corners"] == result["Power"]["corners"] == result["Final"]["corners"]
    assert result["Crossbar"]["bounds"] == (132, 60, 212, 154)
    result["mating"] = compare_pairs(boards)
    result["supports"] = support_axes(boards)
    result["connected_pad_pairs"] = verify_trial(boards["Final"])
    result["reference_plane_samples_total_and_on_GND"] = reference_planes(boards["Final"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boards", nargs=4, type=Path, metavar="PCB",
                        help="Control, Power, Crossbar and Final-Control in this order")
    parser.add_argument("--before", nargs=4, type=Path, metavar="PCB")
    args = parser.parse_args()
    boards = load(args.boards)
    result = measure(boards)
    if args.before:
        before = load(args.before)
        for name, board in boards.items():
            assert electric_identity(before[name]) == electric_identity(board), name
        assert routes(before["Final"]) == routes(boards["Final"])
        result["baseline"] = measure(before)
        assert (result["reference_plane_samples_total_and_on_GND"]
                == result["baseline"]["reference_plane_samples_total_and_on_GND"])
        result["identity_and_trial_copper_equal"] = True
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
