"""Draw images/consultant-diamond.png. Run from the repo root: python3 scripts/consultant_diamond.py"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TEAL, FILL, RING, INK, GREY = "#0d9488", "#d9eeec", "#d4d4dc", "#1f1f23", "#6b6b75"
# clockwise from top: Judgment, Communication, Ownership, Collaboration
dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
labels = [("Judgment", "Think Clearly +\nGet to the Right Answer"),
          ("Communication", "Create Impact with People:\nunderstand"),
          ("Ownership", "Move Work Forward"),
          ("Collaboration", "Create Impact with People:\ntrust")]
example = [4, 4, 3.5, 3]

fig, ax = plt.subplots(figsize=(9, 8), dpi=200)
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
for r in range(1, 6):
    xs = [d[0] * r for d in dirs] + [dirs[0][0] * r]
    ys = [d[1] * r for d in dirs] + [dirs[0][1] * r]
    ax.plot(xs, ys, color=RING, lw=2.2 if r == 5 else 1.0, zorder=1)
for d in dirs:
    ax.plot([0, d[0] * 5], [0, d[1] * 5], color=RING, lw=1.0, zorder=1)
for r in range(1, 6):
    ax.text(0.3, r + 0.05, str(r), color=GREY, fontsize=9, va="bottom", ha="left", zorder=5)
px = [d[0] * v for d, v in zip(dirs, example)]; py = [d[1] * v for d, v in zip(dirs, example)]
ax.fill(px, py, color=FILL, alpha=0.75, zorder=0)
ax.plot(px + [px[0]], py + [py[0]], color=TEAL, lw=3, zorder=3)
ax.scatter(px, py, color=TEAL, s=60, zorder=4)

pos = [((0, 6.15), "center", "bottom"), ((5.6, 0), "left", "center"),
       ((0, -6.0), "center", "top"), ((-5.6, 0), "right", "center")]
for (name, imp), ((x, y), ha, va) in zip(labels, pos):
    if va == "bottom":
        ax.text(x, y + 0.15 + 0.4 * (imp.count("\n") + 1), name, ha=ha, va="bottom", fontsize=15, color=INK)
        ax.text(x, y, imp, ha=ha, va="bottom", fontsize=10, color=GREY)
    elif va == "top":
        ax.text(x, y, name, ha=ha, va="top", fontsize=15, color=INK)
        ax.text(x, y - 0.95, imp, ha=ha, va="top", fontsize=10, color=GREY, multialignment="center")
    else:
        ax.text(x, y + 0.25, name, ha=ha, va="bottom", fontsize=15, color=INK)
        ax.text(x, y - 0.15, imp, ha=ha, va="top", fontsize=10, color=GREY, multialignment="left" if ha == "left" else "right")
ax.text(0, 8.3, "THE CONSULTANT DIAMOND", ha="center", va="bottom", fontsize=20, weight="bold", color=INK)
ax.set_xlim(-10.5, 10.5); ax.set_ylim(-8.6, 9.4); ax.set_aspect("equal"); ax.axis("off")
plt.savefig("images/consultant-diamond.png", bbox_inches="tight", pad_inches=0.3, facecolor="white")
