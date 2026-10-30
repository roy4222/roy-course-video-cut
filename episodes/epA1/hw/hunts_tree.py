# -*- coding: utf-8 -*-
"""
Machine Learning - Assignment 1: Hunt's algorithm
Builds a decision tree with Hunt's algorithm (implemented from scratch, recursive),
using a FIXED attribute order: Gender -> Car Type -> Shirt Size, multi-way splits.

Handling rules (lecture slides 52-53, 61, 101; plus our rules for cases not covered):
  1. All records in D_t belong to the same class  -> leaf labelled with that class.
  2. No attribute left, or all records have identical attribute values
     -> leaf labelled with the majority class of D_t; if the classes tie,
        use the parent node's majority class.
  3. D_t is empty (attribute value not present in the parent's records)
     -> leaf labelled with the parent node's majority class.
  4. Otherwise -> split D_t on the next attribute (multi-way: one child per value)
     and apply the procedure recursively to every child.

Outputs: step log (console + hunts_steps.csv), text tree, tree figures (PNG),
training accuracy.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ data
RAW = [
    (1, "M", "Family", "Small", "C0"),
    (2, "M", "Sports", "Medium", "C0"),
    (3, "M", "Sports", "Medium", "C0"),
    (4, "M", "Sports", "Large", "C0"),
    (5, "M", "Sports", "Extra Large", "C0"),
    (6, "M", "Sports", "Extra Large", "C0"),
    (7, "F", "Sports", "Small", "C0"),
    (8, "F", "Sports", "Small", "C0"),
    (9, "F", "Sports", "Medium", "C0"),
    (10, "F", "Luxury", "Large", "C0"),
    (11, "M", "Family", "Large", "C1"),
    (12, "M", "Family", "Extra Large", "C1"),
    (13, "M", "Family", "Medium", "C1"),
    (14, "M", "Luxury", "Extra Large", "C1"),
    (15, "F", "Luxury", "Small", "C1"),
    (16, "F", "Luxury", "Small", "C1"),
    (17, "F", "Luxury", "Medium", "C1"),
    (18, "F", "Luxury", "Medium", "C1"),
    (19, "F", "Luxury", "Medium", "C1"),
    (20, "F", "Luxury", "Large", "C1"),
]
DATA = pd.DataFrame(RAW, columns=["CustomerID", "Gender", "Car Type", "Shirt Size", "Class"])

ATTR_ORDER = ["Gender", "Car Type", "Shirt Size"]          # fixed order required by the assignment
DOMAIN = {                                                   # all possible values -> multi-way split
    "Gender": ["M", "F"],
    "Car Type": ["Family", "Sports", "Luxury"],
    "Shirt Size": ["Small", "Medium", "Large", "Extra Large"],
}
CLASSES = ["C0", "C1"]

# ------------------------------------------------------------------ helpers
def class_counts(D):
    return {c: int((D["Class"] == c).sum()) for c in CLASSES}

def majority(counts, fallback):
    """Most frequent class; on a tie (or empty set) return the fallback (parent's majority)."""
    best = max(counts.values())
    winners = [c for c in CLASSES if counts[c] == best]
    if best == 0 or len(winners) > 1:
        return fallback, True
    return winners[0], False

def fmt_counts(cnt):
    return f"({cnt['C0']},{cnt['C1']})"

class Node:
    def __init__(self, path, depth, records, counts):
        self.path, self.depth, self.records, self.counts = path, depth, records, counts
        self.attr = None            # split attribute (internal node)
        self.children = {}          # value -> Node
        self.label = None           # class label (leaf)
        self.majority = None        # majority class of D_t (used for empty / tie children)
        self.reason = ""
        self.step = None

STEP_LOG = []

def hunt(D, attrs, path="root", depth=0, parent_majority=None):
    """Hunt's algorithm (recursive). D = records reaching node t, attrs = remaining attributes."""
    cnt = class_counts(D)
    node = Node(path, depth, list(D["CustomerID"]), cnt)
    node.step = len(STEP_LOG) + 1
    maj, tie = majority(cnt, parent_majority)
    node.majority = maj
    entry = {"Step": node.step, "Depth": depth, "Node path": path,
             "Record IDs": ",".join(map(str, node.records)) if len(D) else "(none)",
             "n": len(D), "C0": cnt["C0"], "C1": cnt["C1"]}

    # Case 3: empty set -> parent's majority
    if len(D) == 0:
        node.label = parent_majority
        node.reason = f"empty node -> label with parent's majority class ({parent_majority})"
    # Case 1: all records same class -> pure leaf
    elif cnt["C0"] == 0 or cnt["C1"] == 0:
        node.label = "C0" if cnt["C1"] == 0 else "C1"
        node.reason = f"pure node (all records are {node.label})"
    # Case 2: no attribute left / identical attribute values -> majority (tie -> parent's majority)
    elif not attrs or len(D[attrs].drop_duplicates()) == 1:
        why = "no attribute left" if not attrs else "identical attribute values"
        if len(D[ATTR_ORDER].drop_duplicates()) == 1:
            why += " (records have identical attribute values)"
        node.label = maj
        node.reason = (f"{why}; class tie {fmt_counts(cnt)} -> parent's majority ({maj})" if tie
                       else f"{why}; majority class = {maj}")
    # Case 4: split on the next attribute in the fixed order (multi-way split)
    else:
        a = attrs[0]
        node.attr = a
        parts = []
        for v in DOMAIN[a]:
            Dv = D[D[a] == v]
            parts.append(f"{a}={v}: IDs[{','.join(map(str, Dv['CustomerID'])) or '-'}] {fmt_counts(class_counts(Dv))}")
        node.reason = f"mixed classes -> split on '{a}' (multi-way)"
        entry.update({"Decision": "SPLIT", "Attribute / Label": a, "Reason": node.reason,
                      "Child partitions": " | ".join(parts)})
        STEP_LOG.append(entry)
        print_step(entry)
        for v in DOMAIN[a]:
            child_path = f"{path} > {a}={v}"
            node.children[v] = hunt(D[D[a] == v], attrs[1:], child_path, depth + 1, maj)
        return node

    entry.update({"Decision": "LEAF", "Attribute / Label": node.label, "Reason": node.reason,
                  "Child partitions": ""})
    STEP_LOG.append(entry)
    print_step(entry)
    return node

def print_step(e):
    print(f"[Step {e['Step']:2d}] depth={e['Depth']}  node: {e['Node path']}")
    print(f"          records: {e['Record IDs']}   n={e['n']}   counts (C0,C1)=({e['C0']},{e['C1']})")
    if e["Decision"] == "SPLIT":
        print(f"          -> SPLIT on {e['Attribute / Label']}: {e['Reason']}")
        for p in e["Child partitions"].split(" | "):
            print(f"               - {p}")
    else:
        print(f"          -> LEAF, class = {e['Attribute / Label']}  ({e['Reason']})")
    print()

# ------------------------------------------------------------------ text tree / rules / predict
def tree_text(node, indent="", edge=None):
    lines = []
    head = f"{indent}{edge + ': ' if edge else ''}"
    if node.attr:
        lines.append(f"{head}[{node.attr}] {fmt_counts(node.counts)}")
        for v, ch in node.children.items():
            lines += tree_text(ch, indent + "    ", f"{node.attr}={v}")
    else:
        lines.append(f"{head}Class = {node.label} {fmt_counts(node.counts)}"
                     + ("  *empty" if node.counts['C0'] + node.counts['C1'] == 0 else ""))
    return lines

def rules(node, conds=()):
    if not node.attr:
        return [(" AND ".join(conds), node.label, node.counts)]
    out = []
    for v, ch in node.children.items():
        out += rules(ch, conds + (f"{node.attr} = {v}",))
    return out

def predict(node, row):
    while node.attr:
        node = node.children[row[node.attr]]
    return node.label

# ------------------------------------------------------------------ drawing (from the algorithm's own tree)
def draw(root, fname, max_depth=None, title=None):
    """Draw the tree. Nodes deeper than max_depth are not shown; frontier nodes that are
    still impure are drawn as provisional leaves labelled with their majority class
    (like Fig. 3.6 (a)-(c) in the slides)."""
    pos, leaves = {}, [0]
    def layout(n):
        expand = n.attr and (max_depth is None or n.depth < max_depth)
        if not expand:
            pos[id(n)] = (leaves[0], -n.depth); leaves[0] += 1
            return
        for ch in n.children.values():
            layout(ch)
        xs = [pos[id(ch)][0] for ch in n.children.values()]
        pos[id(n)] = ((min(xs) + max(xs)) / 2, -n.depth)
    layout(root)
    width = max(leaves[0], 1)
    depth_shown = max(-y for _, y in pos.values())
    fig, ax = plt.subplots(figsize=(max(4, width * 1.45), 0.8 + 1.5 * (depth_shown + 1)))
    ax.axis("off")

    def draw_node(n):
        x, y = pos[id(n)]
        expand = n.attr and (max_depth is None or n.depth < max_depth)
        if expand:
            for v, ch in n.children.items():
                cx, cy = pos[id(ch)]
                ax.plot([x, cx], [y - 0.2, cy + 0.2], color="black", lw=1)
                ax.text((x + cx) / 2, (y + cy) / 2, v, ha="center", va="center", fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
                draw_node(ch)
            ax.text(x, y, f"{n.attr}\n{fmt_counts(n.counts)}", ha="center", va="center", fontsize=10,
                    bbox=dict(boxstyle="ellipse,pad=0.35", fc="#e8f0fb", ec="#1f4e79"))
        else:
            empty = n.counts["C0"] + n.counts["C1"] == 0
            lab = n.label if n.label else (n.majority or "C0/C1 tie")
            ax.text(x, y, f"Class = {lab}\n{fmt_counts(n.counts)}" + (" empty" if empty else ""),
                    ha="center", va="center", fontsize=9.5,
                    bbox=dict(boxstyle="square,pad=0.35", fc="#fff4e5" if not empty else "#f2f2f2",
                              ec="#7f3f00" if not empty else "#888888",
                              ls="-" if not empty else "--"))
    draw_node(root)
    ax.set_xlim(-0.8, width - 0.2)
    ax.set_ylim(-depth_shown - 0.45, 0.45)
    if title:
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, fname)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path

# ------------------------------------------------------------------ main
if __name__ == "__main__":
    print("=" * 78)
    print("Hunt's algorithm  |  attribute order:", " -> ".join(ATTR_ORDER), " |  multi-way split")
    print("Counts are shown as (C0, C1)")
    print("=" * 78, "\n")

    root = hunt(DATA, ATTR_ORDER)

    print("=" * 78)
    print("Final decision tree")
    print("=" * 78)
    print("\n".join(tree_text(root)), "\n")

    print("=" * 78)
    print("Decision rules (IF-THEN)")
    print("=" * 78)
    for i, (c, lab, cnt) in enumerate(rules(root), 1):
        print(f"R{i:02d}: IF {c} THEN Class = {lab}   {fmt_counts(cnt)}")
    print()

    DATA["Predicted"] = DATA.apply(lambda r: predict(root, r), axis=1)
    correct = int((DATA["Predicted"] == DATA["Class"]).sum())
    print("=" * 78)
    print(f"Training accuracy: {correct}/{len(DATA)} = {correct / len(DATA):.2%}")
    wrong = DATA[DATA["Predicted"] != DATA["Class"]]
    for _, r in wrong.iterrows():
        print(f"  misclassified: ID {r['CustomerID']} ({r['Gender']}, {r['Car Type']}, {r['Shirt Size']}) "
              f"actual={r['Class']} predicted={r['Predicted']}")
    print("=" * 78, "\n")

    log = pd.DataFrame(STEP_LOG)
    log.to_csv(os.path.join(OUT_DIR, "hunts_steps.csv"), index=False, encoding="utf-8-sig")
    DATA.to_csv(os.path.join(OUT_DIR, "hunts_predictions.csv"), index=False, encoding="utf-8-sig")

    figs = [draw(root, "tree_step_a.png", 0, "(a) root: all 20 records"),
            draw(root, "tree_step_b.png", 1, "(b) split on Gender"),
            draw(root, "tree_step_c.png", 2, "(c) split on Car Type"),
            draw(root, "tree_final.png", None, "(d) split on Shirt Size - final Hunt's tree")]
    print("Saved:", os.path.join(OUT_DIR, "hunts_steps.csv"))
    print("Saved:", os.path.join(OUT_DIR, "hunts_predictions.csv"))
    for f in figs:
        print("Saved:", f)
