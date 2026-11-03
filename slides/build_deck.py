#!/usr/bin/env python3
"""Build the Data Labs deck.

Output: slides/cassandra-data-labs.pptx
Import that file into Google Slides (see slides/README.md).

Requires: python-pptx, Pillow
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = Path(__file__).resolve().parent / ".pydeps"
if DEPS.exists():
    sys.path.insert(0, str(DEPS))

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ASSETS = ROOT / "assets"
BUILD = Path(__file__).resolve().parent / ".build"
OUT = Path(__file__).resolve().parent / "cassandra-data-labs.pptx"

BG = RGBColor(0x0B, 0x1B, 0x2B)
BG_RAISED = RGBColor(0x12, 0x2A, 0x3D)
BG_CODE = RGBColor(0x08, 0x14, 0x20)
CYAN = RGBColor(0x67, 0xE8, 0xF9)
GOLD = RGBColor(0xF0, 0xC1, 0x4A)
WHITE = RGBColor(0xF4, 0xF7, 0xFA)
MUTED = RGBColor(0xB7, 0xC6, 0xD3)
LINE = RGBColor(0x1E, 0x4A, 0x5C)
CORAL = RGBColor(0xF0, 0x8A, 0x7A)

W = Inches(13.333)
H = Inches(7.5)


def _set_run(paragraph, text, size, color, bold=False, font="Arial", italic=False):
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    return run


def _blank(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = BG
    shape.line.fill.background()
    return slide


def _notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def _footer(slide, label):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(7.08), Inches(10.5), Inches(0.28))
    tf = box.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    _set_run(p, label, 11, MUTED)
    box2 = slide.shapes.add_textbox(Inches(10.6), Inches(7.08), Inches(2.2), Inches(0.28))
    p2 = box2.text_frame.paragraphs[0]
    p2.alignment = PP_ALIGN.RIGHT
    _set_run(p2, "Cassandra Data Labs", 11, MUTED)


def _title(slide, text, top=0.32, size=32):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(12.2), Inches(0.7))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _set_run(p, text, size, WHITE, bold=True)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(top + 0.68), Inches(1.4), Inches(0.045)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background()
    return top + 0.9


def _bullets(slide, items, top, size=22, color=WHITE, width=12.2, height=5.2):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(12)
        _set_run(p, item, size, color)
    return box


def _code_block(slide, text, top, height=3.2):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), Inches(top), Inches(12.2), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = BG_CODE
    shape.line.color.rgb = LINE
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.16)
    lines = text.strip("\n").split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(0)
        _set_run(p, line if line else " ", 16, CYAN, font="Courier New")
    return shape


def _style_table(table, header=True):
    for r, row in enumerate(table.rows):
        for cell in row.cells:
            cell.fill.solid()
            cell.fill.fore_color.rgb = BG_RAISED if r == 0 and header else BG_CODE
            cell.margin_left = Inches(0.1)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                for run in p.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(14)
                    run.font.bold = r == 0 and header
                    run.font.color.rgb = GOLD if r == 0 and header else WHITE
            # Cell borders
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            for edge in ("lnL", "lnR", "lnT", "lnB"):
                ln = tcPr.find(qn(f"a:{edge}"))
                if ln is None:
                    ln = tcPr.makeelement(qn(f"a:{edge}"), {})
                    tcPr.append(ln)
                ln.set("w", "6350")
                sf = ln.makeelement(qn("a:solidFill"), {})
                c = sf.makeelement(qn("a:srgbClr"), {"val": "1E4A5C"})
                sf.append(c)
                ln.append(sf)


def prepare_image(name: str) -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    src = ASSETS / name
    dest = BUILD / (Path(name).stem + ".jpg")
    im = Image.open(src).convert("RGB")
    if im.width > 1920:
        height = round(im.height * 1920 / im.width)
        im = im.resize((1920, height), Image.Resampling.LANCZOS)
    im.save(dest, quality=85, optimize=True)
    return dest


def add_title(prs, footer, spec):
    slide = _blank(prs)
    kicker = slide.shapes.add_textbox(Inches(0.7), Inches(1.55), Inches(11), Inches(0.4))
    _set_run(kicker.text_frame.paragraphs[0], spec["kicker"], 16, GOLD, bold=True)
    box = slide.shapes.add_textbox(Inches(0.7), Inches(2.05), Inches(11.5), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _set_run(p, spec["title"], 48, WHITE, bold=True)
    if spec.get("subtitle"):
        p2 = tf.add_paragraph()
        p2.space_before = Pt(12)
        _set_run(p2, spec["subtitle"], 22, MUTED)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(4.55), Inches(1.6), Inches(0.05)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = CYAN
    bar.line.fill.background()
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_section(prs, footer, spec):
    slide = _blank(prs)
    kicker = slide.shapes.add_textbox(Inches(0.7), Inches(2.15), Inches(11), Inches(0.4))
    _set_run(kicker.text_frame.paragraphs[0], spec["kicker"], 16, GOLD, bold=True)
    box = slide.shapes.add_textbox(Inches(0.7), Inches(2.6), Inches(11.5), Inches(1.6))
    tf = box.text_frame
    tf.word_wrap = True
    _set_run(tf.paragraphs[0], spec["title"], 40, WHITE, bold=True)
    if spec.get("subtitle"):
        p2 = tf.add_paragraph()
        p2.space_before = Pt(14)
        _set_run(p2, spec["subtitle"], 20, MUTED)
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_bullets(prs, footer, spec):
    slide = _blank(prs)
    top = _title(slide, spec["title"], size=spec.get("title_size", 30))
    _bullets(slide, spec["items"], top, size=spec.get("size", 22), height=6.0)
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_columns(prs, footer, spec):
    slide = _blank(prs)
    top = _title(slide, spec["title"])
    columns = spec["columns"]
    gap = 0.25
    col_w = (12.2 - gap * (len(columns) - 1)) / len(columns)
    for i, (heading, items) in enumerate(columns):
        left = 0.55 + i * (col_w + gap)
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left),
            Inches(top),
            Inches(col_w),
            Inches(5.15),
        )
        card.fill.solid()
        card.fill.fore_color.rgb = BG_RAISED
        card.line.color.rgb = LINE
        box = slide.shapes.add_textbox(
            Inches(left + 0.25), Inches(top + 0.22), Inches(col_w - 0.45), Inches(4.7)
        )
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _set_run(p, heading, 18, GOLD, bold=True)
        for item in items:
            bp = tf.add_paragraph()
            bp.space_before = Pt(10)
            _set_run(bp, item, 16, WHITE)
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_table(prs, footer, spec):
    slide = _blank(prs)
    top = _title(slide, spec["title"])
    rows = [spec["headers"]] + spec["rows"]
    n_rows = len(rows)
    n_cols = len(spec["headers"])
    table_height = min(5.4, 0.58 * n_rows)
    shape = slide.shapes.add_table(
        n_rows, n_cols, Inches(0.55), Inches(top + 0.1), Inches(12.2), Inches(table_height)
    )
    table = shape.table
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.cell(r, c).text = value
    _style_table(table)
    if spec.get("foot"):
        box = slide.shapes.add_textbox(Inches(0.55), Inches(top + table_height + 0.3), Inches(12.2), Inches(0.6))
        box.text_frame.word_wrap = True
        _set_run(box.text_frame.paragraphs[0], spec["foot"], 16, MUTED, italic=True)
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_code(prs, footer, spec):
    slide = _blank(prs)
    top = _title(slide, spec["title"], size=28)
    if spec.get("lead"):
        lead = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(12.2), Inches(0.4))
        _set_run(lead.text_frame.paragraphs[0], spec["lead"], 16, MUTED)
        top += 0.45
    _code_block(slide, spec["code"], top, height=spec.get("height", 4.4))
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_lab(prs, footer, spec):
    slide = _blank(prs)
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), Inches(0.28), Inches(2.5), Inches(0.38)
    )
    pill.fill.solid()
    pill.fill.fore_color.rgb = GOLD
    pill.line.fill.background()
    tf = pill.text_frame
    tf.word_wrap = False
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    _set_run(tf.paragraphs[0], f"LAB  ·  {spec['minutes']} MIN", 13, BG, bold=True)
    box = slide.shapes.add_textbox(Inches(3.2), Inches(0.26), Inches(9.5), Inches(0.45))
    _set_run(box.text_frame.paragraphs[0], spec["title"], 26, WHITE, bold=True)
    _bullets(slide, spec["steps"], 0.9, size=20, height=4.6)
    see = slide.shapes.add_textbox(Inches(0.55), Inches(6.15), Inches(12.2), Inches(0.8))
    see.text_frame.word_wrap = True
    p = see.text_frame.paragraphs[0]
    _set_run(p, "You should see  ", 16, GOLD, bold=True)
    _set_run(p, spec["see"], 16, WHITE)
    _footer(slide, footer)
    _notes(slide, spec["notes"])


def add_image(prs, footer, spec):
    slide = _blank(prs)
    path = prepare_image(spec["file"])
    slide.shapes.add_picture(str(path), 0, 0, W, H)
    _notes(slide, spec["notes"] + f"\n\nPoster: assets/{spec['file']}")


def build(spec_list):
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    prs.core_properties.title = "Cassandra and DSE — Data Labs"
    prs.core_properties.subject = "Four sessions of two hours. DSE explained, labs on open-source Cassandra."
    prs.core_properties.category = "Training"
    footer = "Data Labs"
    for spec in spec_list:
        kind = spec["type"]
        if kind == "section":
            footer = spec.get("footer", spec["title"])
        if kind == "title":
            add_title(prs, footer, spec)
        elif kind == "section":
            add_section(prs, footer, spec)
        elif kind == "bullets":
            add_bullets(prs, footer, spec)
        elif kind == "columns":
            add_columns(prs, footer, spec)
        elif kind == "table":
            add_table(prs, footer, spec)
        elif kind == "code":
            add_code(prs, footer, spec)
        elif kind == "lab":
            add_lab(prs, footer, spec)
        elif kind == "image":
            add_image(prs, footer, spec)
        else:
            raise SystemExit(f"unknown slide type {kind}")
    prs.save(OUT)
    return len(spec_list)


def deck():
    return [
        {
            "type": "title",
            "kicker": "DATA LABS  ·  4 SESSIONS  ×  2 HOURS",
            "title": "Cassandra and DSE",
            "subtitle": "A common foundation, then the application track.\nLabs run on open-source Cassandra. DSE is explained, not labbed.",
            "notes": "Open by naming the two phases and the rule of the room: same three-node cluster all week, DSE is discussion only. Full script lives in sessions/. This deck is the clock and the pictures. Import into Google Slides if you want a shared presenter file; speaker notes come with it.",
        },
        {
            "type": "columns",
            "title": "Who this is for",
            "columns": [
                (
                    "Phase 1 — sessions 1 and 2",
                    [
                        "Developers",
                        "Platform engineers",
                        "SRE",
                        "Support",
                        "Goal: one architectural picture of Cassandra and of DSE.",
                    ],
                ),
                (
                    "Phase 2 — sessions 3 and 4",
                    [
                        "Development teams",
                        "Architects",
                        "Technical leads",
                        "Goal: schemas and drivers that stay fast.",
                        "Assumes the Phase 1 vocabulary.",
                    ],
                ),
            ],
            "notes": "If Phase 2 is a different group, spend the first 15 minutes of session 3 on placement (session 1, sections 4 and 5) and cut the optional clustering-order lab.",
        },
        {
            "type": "bullets",
            "title": "How a session runs",
            "items": [
                "Teach from this deck. The lab steps are on the gold slides, in the block they illustrate.",
                "Do not save the labs for a separate hour at the end.",
                "Each session has one cut if you are behind. Take that cut. Do not drop the lab the next session needs.",
                "The reference modules are extra. They are not a fifth session.",
                "Full commands, when a slide abbreviates them: sessions/.",
            ],
            "notes": "Point at the repo. Cluster start and reset are in the README. Session 1 creates lab_ks. Leave the cluster up between sessions if the room allows.",
        },
        {
            "type": "table",
            "title": "One cluster for every lab",
            "headers": ["Setting", "This room"],
            "rows": [
                ["Nodes", "cassandra-1, cassandra-2, cassandra-3"],
                ["Datacenter", "datacenter1"],
                ["Snitch", "GossipingPropertyFileSnitch"],
                ["Keyspace", "lab_ks  ·  NetworkTopologyStrategy  ·  RF 3"],
                ["First table", "events (user_id, event_time)"],
                ["Client port", "localhost:9042 on cassandra-1"],
            ],
            "foot": "RF 3 on three nodes means every partition has a replica on every node. Say that once. Session 2 depends on it.",
            "notes": "SimpleStrategy is the wrong habit here because it ignores datacenters. If someone already created lab_ks with SimpleStrategy, drop it and recreate.",
        },
        {
            "type": "section",
            "kicker": "PHASE 1  ·  SESSION 1  ·  2 HOURS",
            "title": "Common foundation",
            "subtitle": "What it is, how DSE differs, and where a partition lives.",
            "footer": "Session 1  ·  Common foundation",
            "notes": "Audience is the whole room: developers, platform, SRE, support. Outcomes: when Cassandra fits, the four deployment choices, a running cluster, and getendpoints.",
        },
        {
            "type": "bullets",
            "title": "Session 1",
            "size": 22,
            "items": [
                "0–15    What Cassandra is for, and when it is the wrong tool",
                "15–35   OSS, DSE, HCD, Astra  —  DSE is talk only",
                "35–70   Lab: cluster up, lab_ks, events",
                "70–95   Masterless ring",
                "95–120  Lab: any node coordinates, getendpoints",
            ],
            "notes": "If you are behind, skip the optional describecluster at the end. Do not skip getendpoints. You leave able to say what the partition key controls.",
        },
        {
            "type": "columns",
            "title": "Where it fits",
            "columns": [
                (
                    "A strong fit",
                    [
                        "Live reads and writes at high throughput.",
                        "Events, time series, catalogs, sessions, messaging metadata, IoT ingest.",
                        "No master. Consistency chosen per request.",
                        "Availability across node loss, when RF and the consistency level match.",
                    ],
                ),
                (
                    "A poor fit",
                    [
                        "Ad-hoc joins across arbitrary tables.",
                        "Multi-key transactions as the default model.",
                        "A small dataset with no availability need. Use SQL.",
                        "A warehouse. Export to one. Do not query like one.",
                    ],
                ),
            ],
            "notes": "LWT exists for a narrow compare-and-set. It is not a SQL transaction habit. You will show one in session 4, not today.",
        },
        {
            "type": "table",
            "title": "Four ways to run it",
            "headers": ["", "Who operates", "Beyond CQL", "In this room"],
            "rows": [
                ["OSS Cassandra", "You", "The database", "Every lab"],
                ["DSE", "You, vendor build", "Search, Analytics, Graph, ops tools", "Explain only"],
                ["HCD", "You, on Kubernetes", "Supported platform", "Explain only"],
                ["Astra DB", "DataStax", "Managed service", "Explain only"],
            ],
            "foot": "Same CQL, same drivers, same partition rules. The difference is who runs the nodes and what else shares them.",
            "notes": "DSE line most estates still run: 6.8 / 6.9 on a Cassandra 4.x core. A schema and a driver config that are correct here stay correct against DSE contact points.",
        },
        {
            "type": "bullets",
            "title": "DSE, without a DSE lab",
            "items": [
                "Supported Cassandra you still operate. The ring, RF, consistency, CQL, and the storage engine match this cluster.",
                "OpsCenter and Lifecycle Manager watch repair, backup, and metrics. Newer planes use Mission Control.",
                "Auth, roles, and encryption are packaged, often with LDAP or Kerberos.",
                "Search (Solr), Analytics (Spark), and Graph share the nodes. They change capacity. They do not replace the partition key.",
                "A DSE node with those components on is not “Cassandra plus a logo.”",
            ],
            "notes": "Do not open OpsCenter. Do not create a Search core. The point is that support and SRE can tell a Cassandra fact from a DSE product. Developers should hear that modeling does not change.",
        },
        {
            "type": "columns",
            "title": "Two minutes, no cluster",
            "columns": [
                (
                    "Plain Cassandra",
                    [
                        "UN or DN, load, tokens.",
                        "Replication factor and the snitch.",
                        "A consistency level on the statement.",
                        "Hints, read repair, nodetool repair.",
                    ],
                ),
                (
                    "Only because it is DSE",
                    [
                        "OpsCenter repair service.",
                        "A Solr core on the node.",
                        "A Spark worker beside Cassandra.",
                        "Graph workloads on the same hosts.",
                    ],
                ),
            ],
            "notes": "Ask the room to sort a status page. UN is Cassandra. A Search core is DSE. Same question works for support tickets all year.",
        },
        {
            "type": "lab",
            "minutes": "35",
            "title": "Start the cluster and create lab_ks",
            "steps": [
                "From the repo root: docker compose up -d",
                "nodetool status on cassandra-1 until three rows say UN.",
                "cqlsh on cassandra-1. cluster_name is training-lab.",
                "Create lab_ks with NetworkTopologyStrategy, datacenter1: 3.",
                "Create events. user_id partitions. event_time clusters.",
            ],
            "see": "DESCRIBE KEYSPACE lab_ks shows datacenter1: 3. Not SimpleStrategy.",
            "notes": "Full CQL is the next slide and in sessions/01. If the keyspace already exists with SimpleStrategy, DROP KEYSPACE lab_ks and recreate. Heap is 1G per node; the room wants about 6 GB free.",
        },
        {
            "type": "code",
            "title": "The schema for the rest of the course",
            "lead": "Snitch is already GossipingPropertyFileSnitch. Match it.",
            "height": 4.6,
            "code": """CREATE KEYSPACE lab_ks
  WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3 };

CREATE TABLE events (
  user_id uuid,
  event_time timestamp,
  payload text,
  PRIMARY KEY (user_id, event_time) );""",
            "notes": "user_id is the only thing that is hashed. event_time orders rows inside that partition. RF 3 and three nodes: every key lives on every node. Say it.",
        },
        {
            "type": "image",
            "file": "architecture-masterless.png",
            "notes": "No special node. Every node can coordinate. Commit log and memtable are local; the ring is the system. On DSE the ring works the same way. About 8 minutes, then the next two posters. Do not read every label.",
        },
        {
            "type": "image",
            "file": "architecture-peers-vs-master-slave.png",
            "notes": "Contrast with a primary: one writer is a bottleneck and a single failure. Scale by adding peers, not by buying a bigger master. One minute.",
        },
        {
            "type": "image",
            "file": "architecture-consistent-hashing-vnodes.png",
            "notes": "Partition key hashes to a token. Replicas walk the ring from there. Vnodes are many small ranges per machine so membership changes move less data. NTS uses the snitch so replicas respect racks and DCs. SimpleStrategy does not.",
        },
        {
            "type": "lab",
            "minutes": "25",
            "title": "Any node coordinates. The key picks replicas.",
            "steps": [
                "cqlsh on cassandra-2. DESCRIBE TABLES. events is there.",
                "Insert one row with a fixed user_id.",
                "nodetool getendpoints lab_ks events <that-user_id>",
                "Optional: nodetool describecluster. Name and partitioner only.",
            ],
            "see": "Three addresses. In this lab that is the whole cluster. In production it is three of many, and a different key is a different three.",
            "notes": "There is no primary to connect to. Drivers in session 4 still want a local DC and token-aware routing. That is load balancing, not a master. UUID for the demo is 123e4567-e89b-12d3-a456-426614174000 if you want everyone on the same key. Cut describecluster first.",
        },
        {
            "type": "bullets",
            "title": "One sentence before you break",
            "items": [
                "Developer: the partition key is what gets hashed.",
                "Platform: the keyspace names datacenter1 because that is the name the snitch reports.",
                "SRE: there is no master. RF 3 is what survives a lost node, together with the consistency level.",
                "Support: UN means up and normal. getendpoints answers “where is this key?”",
            ],
            "notes": "Leave the cluster up. Next session stops cassandra-3 on purpose. If the room must reboot: docker compose stop, not down -v.",
        },
        {
            "type": "section",
            "kicker": "PHASE 1  ·  SESSION 2  ·  2 HOURS",
            "title": "Consistency, topology, storage",
            "subtitle": "How much agreement a request needs, and what a lost node actually does.",
            "footer": "Session 2  ·  Consistency and storage",
            "notes": "Requires lab_ks from session 1. You will trace one write, read the snitch, flush an SSTable, and stop a node. You will name repair. You will not run it.",
        },
        {
            "type": "bullets",
            "title": "Session 2",
            "items": [
                "0–20     CAP and consistency levels",
                "20–45    Lab: ONE versus QUORUM, one trace",
                "45–65    Gossip, the snitch, multi-DC",
                "65–80    Lab: describecluster and the snitch",
                "80–100   Storage engine, and a flush",
                "100–120  Lab: stop cassandra-3",
            ],
            "notes": "If you are behind, skip the second trace. Do not skip the node-down lab. Tombstone and LWT labs are session 4.",
        },
        {
            "type": "image",
            "file": "architecture-cap-theorem.png",
            "notes": "Under a partition you do not get linearizability everywhere and an answer from every side. Cassandra keeps serving and lets the statement say how many replicas must agree. DSE uses the same levels. A Search query is not a consistency level.",
        },
        {
            "type": "table",
            "title": "What you actually ask for",
            "headers": ["Level", "RF = 3, one DC", "Use when"],
            "rows": [
                ["ONE", "1 replica", "Latency first. Stale reads are acceptable."],
                ["QUORUM", "2 of 3", "Default for correctness in one DC."],
                ["LOCAL_QUORUM", "Quorum in the coordinator’s DC", "Production multi-DC. Same as QUORUM here."],
                ["ALL", "Every replica", "Rare. Any down replica fails the statement."],
            ],
            "foot": "QUORUM read plus QUORUM write: the sets overlap, so a successful read sees the latest successful write. ONE plus ONE does not.",
            "notes": "Write R + W > RF on the board if the poster did not. LOCAL_QUORUM is the level the driver will use in session 4.",
        },
        {
            "type": "image",
            "file": "architecture-tunable-consistency.png",
            "notes": "Consistency is per statement, not a cluster mode. The healthy cluster hides the difference. The trace and the stopped node show it.",
        },
        {
            "type": "lab",
            "minutes": "25",
            "title": "Feel a consistency level",
            "steps": [
                "CONSISTENCY ONE, then a small SELECT. Then QUORUM, same SELECT.",
                "The cqlsh prompt shows the level. Both succeed while everyone is up.",
                "TRACING ON. One INSERT at QUORUM. TRACING OFF.",
                "Name the coordinator waiting for replica acknowledgements.",
            ],
            "see": "A trace where the coordinator does not return at the first local write.",
            "notes": "A second trace at ONE is the cut. user_id ending 174001, payload trace-quorum, is in the session file if you want a shared key. Put CONSISTENCY back to QUORUM before you leave the shell.",
        },
        {
            "type": "image",
            "file": "architecture-gossip-failure-detection.png",
            "notes": "Gossip is membership, health, schema, and the token map. It is not the data path. Phi accrual is why one delayed packet does not mark a node dead. The failure lab will wait on this. OpsCenter watches the same state. It does not replace it.",
        },
        {
            "type": "image",
            "file": "architecture-topology-multi-dc.png",
            "notes": "The snitch maps rack and datacenter. NTS places replicas from that map. Clients use LOCAL_* so a request does not wait on the other region. This lab is one DC on purpose. The snitch is already the one you keep when a second DC appears. SimpleSnitch would throw that away.",
        },
        {
            "type": "lab",
            "minutes": "15",
            "title": "Name, partitioner, snitch",
            "steps": [
                "nodetool describecluster",
                "nodetool gossipinfo | head -40",
                "grep endpoint_snitch in cassandra.yaml on cassandra-1",
            ],
            "see": "training-lab, Murmur3Partitioner, peer rows, GossipingPropertyFileSnitch.",
            "notes": "failuredetector is optional. Ask why this single-DC lab still refuses SimpleSnitch and SimpleStrategy: the day you add a datacenter, the strategy and the snitch are already right. Answer belongs in one sentence from the room.",
        },
        {
            "type": "image",
            "file": "architecture-storage-write-path-lsm.png",
            "notes": "Commit log for durability, memtable for the sorted buffer, flush to an immutable SSTable. Fast because it is sequential. Do not linger. Next poster is the read.",
        },
        {
            "type": "image",
            "file": "architecture-storage-read-path.png",
            "notes": "Read merges memtable and SSTables. Bloom filters skip files. Last write wins by timestamp. Compaction exists so a read touches fewer files. Click the compaction poster only if you have a minute.",
        },
        {
            "type": "image",
            "file": "architecture-storage-tombstones.png",
            "notes": "A delete is a write. Say that, and say the lab is session 4. Do not run the delete today. gc_grace_seconds is why the marker stays: an offline replica still has to learn about it.",
        },
        {
            "type": "lab",
            "minutes": "10",
            "title": "Flush a memtable",
            "steps": [
                "INSERT one events row, payload flush-lab.",
                "nodetool flush lab_ks events on cassandra-1.",
                "List the table directory under /var/lib/cassandra/data/lab_ks/.",
            ],
            "see": "A file whose name ends in -Data.db. That is an SSTable.",
            "notes": "This is the picture, on disk, on this node. Compaction stats are in the reference module. Skip them.",
        },
        {
            "type": "image",
            "file": "architecture-hints-repair.png",
            "notes": "Three ways replicas converge without the client doing the work: hinted handoff, read repair, and anti-entropy repair (nodetool repair -pr). You will see the hint directory. You will not run repair. DSE’s repair service schedules that third path. The mechanism is still repair.",
        },
        {
            "type": "lab",
            "minutes": "20",
            "title": "Stop one node",
            "steps": [
                "docker compose stop cassandra-3. Wait until status shows it down.",
                "CONSISTENCY ALL, then INSERT. It fails. ALL needs the down replica.",
                "CONSISTENCY ONE, then INSERT. It succeeds.",
                "List /var/lib/cassandra/hints/ on cassandra-1. Start cassandra-3. Wait for UN.",
            ],
            "see": "A failed ALL, a successful ONE, and a hint file for the down replica. Replay can take a minute.",
            "notes": "Every partition includes cassandra-3 because RF is 3. Hints are stored on the coordinator, not on the dead node. The first ALL may sit until the failure detector convicts the node. Set the shell back to QUORUM. Throwaway cluster only.",
        },
        {
            "type": "bullets",
            "title": "Three questions, no new commands",
            "items": [
                "Why is there no master in this cluster?",
                "What do quorum reads and quorum writes guarantee about overlap when RF is 3?",
                "Name two ways replicas converge without the client reading.",
            ],
            "notes": "Accept hints, read repair, or anti-entropy repair for the third. Phase 1 is done. Phase 2 does not operate gossip or failover. It uses this vocabulary.",
        },
        {
            "type": "image",
            "file": "architecture-summary.png",
            "notes": "Leave this up as people stand. If someone wants the repair command for later: nodetool repair -pr lab_ks. Not now.",
        },
        {
            "type": "section",
            "kicker": "PHASE 2  ·  SESSION 3  ·  2 HOURS",
            "title": "Query-driven design",
            "subtitle": "Each production query is a primary key. That partition stays bounded.",
            "footer": "Session 3  ·  Query-driven design",
            "notes": "Developers, architects, technical leads. If they missed Phase 1, do placement first and cut the optional DESC lab.",
        },
        {
            "type": "bullets",
            "title": "Session 3",
            "items": [
                "0–20     The rule: one table per production query",
                "20–40    Four steps, then the primary key",
                "40–75    Lab: one partition, many rows, one range",
                "75–95    Hot partitions and wide partitions",
                "95–115   Lab: endpoints, and optional DESC order",
                "115–120  Write one query on paper",
            ],
            "notes": "Cut the clustering-order lab first. Do not skip the range query. TTL is named here and labbed in session 4.",
        },
        {
            "type": "image",
            "file": "modeling-relational-vs-cassandra.png",
            "notes": "Relational habit starts from entities and ends in joins. Cassandra habit starts from the queries. If you cannot write equality on the partition key plus an optional clustering range, in order, you do not have the query yet. Read the gold bar aloud.",
        },
        {
            "type": "image",
            "file": "modeling-four-step-process.png",
            "notes": "1 access patterns, including whether the read must see the latest write. 2 partition key. 3 clustering. 4 another table when the second pattern needs a different partition key. Duplication is step 4, and session 4 writes both tables.",
        },
        {
            "type": "image",
            "file": "modeling-primary-key-structure.png",
            "notes": "The poster draws extra parentheses around user_id. The table we created is PRIMARY KEY (user_id, event_time): user_id partitions, event_time clusters. Extra parentheses mean a composite partition key, which is the next slide.",
        },
        {
            "type": "columns",
            "title": "Two ways to add a column to the key",
            "columns": [
                (
                    "Stops one user growing forever",
                    [
                        "PRIMARY KEY ((user_id, day), event_time)",
                        "user_id and day are hashed together.",
                        "One user’s history is many partitions.",
                        "The query must know the day.",
                    ],
                ),
                (
                    "Collects the whole day on one replica set",
                    [
                        "PRIMARY KEY (day, event_time)",
                        "Every writer for “today” hits one partition.",
                        "That is a hot key, not a model.",
                        "Session 4 uses (day, bucket) instead.",
                    ],
                ),
            ],
            "notes": "Bucketing is how you keep a time query without a single hot partition. Do not let the room leave thinking PARTITION BY day is the lesson.",
        },
        {
            "type": "lab",
            "minutes": "35",
            "title": "One user, three times, one range",
            "steps": [
                "DESCRIBE TABLE events. Name the partition key before you insert.",
                "Three rows, same user_id, event_time on two different days.",
                "SELECT by user_id only. Rows come back in event_time order.",
                "Add AND event_time > a timestamp in the middle. Two rows, not a scan of other users.",
            ],
            "see": "A partition-scoped range. Equality on the partition key, then the clustering column, in that order.",
            "notes": "Shared user_id in the session file: 123e4567-e89b-12d3-a456-4266141740bb with morning, afternoon, and next-day payloads. A filter on payload is tomorrow’s anti-pattern. Do not demonstrate it yet.",
        },
        {
            "type": "image",
            "file": "modeling-healthy-vs-hot-partitions.png",
            "notes": "RF and consistency do not spread a bad key. A hot partition is one key taking the traffic. Its replicas glow. The rest of the cluster looks idle. getendpoints will not save you in this three-node lab, because every key maps to every node. Say that before the lab.",
        },
        {
            "type": "image",
            "file": "modeling-wide-partitions.png",
            "notes": "Wide means huge rows or a huge payload under one key. Reads, repair, and compaction all pay. Mitigations to say out loud: bucket, TTL only when the product may forget the row, and honest cardinality. TTL becomes a tombstone. It is not free. Lab is next session.",
        },
        {
            "type": "image",
            "file": "modeling-clustering-order.png",
            "notes": "Ranges are =, >, <, BETWEEN, in primary-key order. Sort order is chosen when you create the table. ORDER BY in the query does not invent a new order. Latest-first is CLUSTERING ORDER BY (event_time DESC).",
        },
        {
            "type": "lab",
            "minutes": "20",
            "title": "Where the key lives. Optional DESC.",
            "steps": [
                "getendpoints for the user_id you just inserted.",
                "Say which part of the key was hashed, and which part only ordered rows.",
                "Optional: a tiny table with CLUSTERING ORDER BY (seq DESC). Read it.",
                "2 comes back before 1. That is a schema choice.",
            ],
            "see": "Three endpoints again. A second user id can map to the same three nodes here. Do not “fix” the model because of that.",
            "notes": "Cut the DESC table first. Full CREATE is in sessions/03 under dm_cluster_demo. Latest-first for a UI is the point of the optional lab, in one sentence.",
        },
        {
            "type": "bullets",
            "title": "On paper, five minutes",
            "items": [
                "Write the CQL, not the prose.",
                "The 20 latest events for one known user.",
                "A passing answer restricts user_id with equality.",
                "Latest-first needs CLUSTERING ORDER BY (event_time DESC), or the app reverses an ascending page and may read too much.",
                "LIMIT 20 without the partition key is not an answer.",
            ],
            "notes": "Collect two answers if you have time. Tomorrow you build the second query, the one this table cannot serve: a slice of a day across users.",
        },
        {
            "type": "section",
            "kicker": "PHASE 2  ·  SESSION 4  ·  2 HOURS",
            "title": "CQL, drivers, and the traps",
            "subtitle": "Tombstones, TTL, a second table, and a driver that states its consistency.",
            "footer": "Session 4  ·  CQL and drivers",
            "notes": "Same audience. Requires the three rows from session 3. Still the open-source cluster. The driver settings are the ones you point at DSE.",
        },
        {
            "type": "bullets",
            "title": "Session 4",
            "items": [
                "0–20     CQL the application actually sends",
                "20–45    Lab: a delete tombstone, then TTL",
                "45–70    Lab: second table, dual write",
                "70–95    Lab: ALLOW FILTERING, then one LWT",
                "95–120  Driver knobs, then the Python lab",
            ],
            "notes": "If you are behind, skip the LWT. Do not skip TTL or the driver.",
        },
        {
            "type": "bullets",
            "title": "CQL looks like SQL and then refuses it",
            "size": 20,
            "items": [
                "INSERT and UPDATE are upserts. Last write wins by timestamp. IF is the exception.",
                "The partition key is equality. Clustering predicates come next, in order, with no gap.",
                "There are no joins. The second query is a second table, and you write both.",
                "A logged batch is not a bulk loader. An unlogged batch belongs to one partition.",
                "Paging belongs in the driver. Prepare the statement. Set consistency on the statement.",
            ],
            "notes": "Schema replication is RF. The driver chooses LOCAL_QUORUM or ONE per call. On DSE you use the same drivers. You change contact points and local DC, not the modeling rules. Types, collections, and counters are not this session.",
        },
        {
            "type": "image",
            "file": "modeling-tombstones-deletes.png",
            "notes": "The row disappears from SELECT. The SSTable is not edited in place. The marker stays for gc_grace_seconds, often 10 days, so a replica that was offline can still learn the delete. A partition full of dead rows is a slow partition.",
        },
        {
            "type": "code",
            "title": "TTL is a scheduled tombstone",
            "lead": "Do not wait 60 seconds. TTL() is the countdown. Leave events without a default TTL.",
            "height": 3.6,
            "code": """CREATE TABLE ttl_demo (id text PRIMARY KEY, payload text);

INSERT INTO ttl_demo (id, payload)
VALUES ('short', 'gone-soon') USING TTL 60;

SELECT id, payload, TTL(payload)
FROM ttl_demo WHERE id = 'short';""",
            "notes": "When the countdown hits zero, Cassandra writes a tombstone and gc_grace applies again. TTL does not fix a hot key. If every row in one partition expires together, you scheduled a delete storm. Use it for sessions and ephemeral events, where the product may forget the row.",
        },
        {
            "type": "lab",
            "minutes": "25",
            "title": "Delete, then a countdown",
            "steps": [
                "INSERT a known events row. DELETE it by the full primary key. SELECT the partition.",
                "The row is gone from the result. Disk was not punched.",
                "Create ttl_demo. INSERT … USING TTL 60.",
                "SELECT TTL(payload). It is a positive number under 60.",
            ],
            "see": "A missing row, and a live cell that already knows when it will die.",
            "notes": "Full DELETE coordinates are in sessions/04, user_id ending 174099, time 2020-06-01. Scratch table so the shared events rows stay. default_time_to_live is the same mechanism at table level. Mention it. Do not set it on events.",
        },
        {
            "type": "image",
            "file": "modeling-denormalization-fan-out.png",
            "notes": "The application writes both tables and has a story when the second write fails. Cassandra will not keep them aligned. A Search index on DSE is not a substitute for the table that serves the known query.",
        },
        {
            "type": "code",
            "title": "A day is not a partition key",
            "lead": "bucket is hash(user_id) % N in production. The lab uses 0. user_id is in the clustering key so one timestamp can hold two events.",
            "height": 3.5,
            "code": """CREATE TABLE events_by_day (
  day text, bucket int, event_time timestamp,
  user_id uuid, payload text,
  PRIMARY KEY ((day, bucket), event_time, user_id)
) WITH CLUSTERING ORDER BY (event_time DESC, user_id ASC);""",
            "notes": "Query: WHERE day = ? AND bucket = ? LIMIT 20. The user history query stays on events. Same logical write, two statements. A logged batch across partitions is optional and expensive. Do not teach it as the importer.",
        },
        {
            "type": "lab",
            "minutes": "25",
            "title": "Write both tables",
            "steps": [
                "Create events_by_day as on the previous slide.",
                "Insert one event into events and the same event into events_by_day.",
                "Read it by user_id. Read it by day and bucket.",
                "Say what the application does if the second insert fails.",
            ],
            "see": "The same payload from both tables. Two queries, two partition keys.",
            "notes": "Shared values in the session file: user …740bb, day 2025-04-01, bucket 0, payload dual-write. Ask who owns retry. The database does not.",
        },
        {
            "type": "image",
            "file": "modeling-anti-patterns.png",
            "notes": "The next lab makes the first query fail on purpose. ALLOW FILTERING makes it succeed on tiny data and scatter-gather on real data. A secondary index is not the design fix. SAI, the default index in Cassandra 5 and available in DSE, is more efficient and still is not a partition key you know in advance.",
        },
        {
            "type": "lab",
            "minutes": "25",
            "title": "The query the schema refused",
            "steps": [
                "SELECT by payload alone. It fails. The coordinator will not scan the cluster.",
                "Add ALLOW FILTERING. It can succeed here because the table is tiny.",
                "Do not CREATE INDEX to “fix” the hot path. Build a table whose key is the lookup.",
                "Optional: one INSERT … IF NOT EXISTS, run twice. [applied] true, then false.",
            ],
            "see": "A rejected query, a dangerous success, and — if you had time — a compare-and-set.",
            "notes": "Skip LWT if the clock slipped. LWT is several round trips and it contends on a hot partition. It is not how you keep events and events_by_day in sync. Accord in Cassandra 5 is a different write path. We do not lab it, and it does not make a bad partition key cheap. Poster for LWT is next if you do the optional step.",
        },
        {
            "type": "image",
            "file": "architecture-lwt-paxos.png",
            "notes": "Show this only if you ran the IF NOT EXISTS. Otherwise skip the slide. Paxos rounds are the cost. Idempotent writes and a spread-out key come first.",
        },
        {
            "type": "table",
            "title": "The driver is where the rules become code",
            "headers": ["Knob", "This lab", "Why"],
            "rows": [
                ["Contact points", "127.0.0.1:9042", "Bootstrap only. The driver discovers the peers."],
                ["Load balancing", "Token-aware, DC-aware, local DC datacenter1", "Prefer a replica in the local DC."],
                ["Consistency", "LOCAL_QUORUM on the statement", "The overlap rule from session 2."],
                ["Prepare", "Insert and select by user_id", "One parse. Bound values."],
                ["Fetch size", "100 in the script", "Paging is the driver’s job."],
            ],
            "foot": "Retries must not blindly repeat a non-idempotent write. Same driver against DSE. Change contact points and local_dc.",
            "notes": "Do not invent a retry policy in the last ten minutes. Read the script with them. The policies are the lesson.",
        },
        {
            "type": "lab",
            "minutes": "25",
            "title": "One prepared write and the read after it",
            "steps": [
                "On the host: pip install cassandra-driver",
                "python labs/driver_basics.py",
                "Read the file while it runs. Find local_dc and LOCAL_QUORUM.",
            ],
            "see": "payload=driver-lab and consistency=LOCAL_QUORUM. A missing lab_ks means session 1 did not finish.",
            "notes": "The script inserts a random user_id and reads it back. It also prints release_version at LOCAL_ONE so a non-prepared statement is still explicit. If pip is blocked, walk the file on the projector. The lab is the settings, not the printout.",
        },
        {
            "type": "image",
            "file": "modeling-preflight-checklist.png",
            "notes": "Close on the checklist, answered for events and events_by_day. Exact CQL for each hot path. Every read partition-scoped. Which partition could grow without a bound, and what the bucket is. Where TTL or deletes churn. What the driver set for local DC and consistency.",
        },
        {
            "type": "bullets",
            "title": "Left for later, on purpose",
            "items": [
                "No OpsCenter, Search, Analytics, or Graph. DSE was session 1.",
                "No repair drill and no multi-DC failover. Those stay in the reference modules.",
                "No Accord lab. Cassandra 5 transactions do not replace this data model.",
                "No index syntax drill. The hot path got a table.",
            ],
            "notes": "Point people who want more at architecture/ and data-modeling/. Thank them. The deck can stay on the checklist poster if you prefer to end on the picture. This slide is the boundary of the eight hours.",
        },
        {
            "type": "title",
            "kicker": "DATA LABS",
            "title": "Same model on DSE.",
            "subtitle": "Different contact points. Same partition key, same consistency, same driver.\nThe cluster you ran was the lesson.",
            "notes": "End. Repo: sessions/ for the scripts, architecture/ and data-modeling/ for the long form, slides/cassandra-data-labs.pptx for this deck.",
        },
    ]


def main():
    # add_two is unused; columns covers that layout.
    n = build(deck())
    print(f"wrote {OUT} ({n} slides, {OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
