const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, LevelFormat, BorderStyle, WidthType, ShadingType,
        VerticalAlign, HeadingLevel, PageBreak } = require('docx');
const fs = require('fs');

// Borders
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// Helper functions
const headerCell = (text, width) => new TableCell({
  borders: cellBorders,
  width: { size: width, type: WidthType.DXA },
  shading: { fill: "002E5D", type: ShadingType.CLEAR },
  verticalAlign: VerticalAlign.CENTER,
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 22 })]
  })]
});

const dataCell = (text, width) => new TableCell({
  borders: cellBorders,
  width: { size: width, type: WidthType.DXA },
  children: [new Paragraph({
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22 })]
  })]
});

const emptyCell = (width, height = 400) => new TableCell({
  borders: cellBorders,
  width: { size: width, type: WidthType.DXA },
  children: [new Paragraph({ spacing: { before: height, after: height }, children: [] })]
});

const sectionHeader = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 300, after: 120 },
  children: [new TextRun({ text, bold: true, size: 28, color: "002E5D" })]
});

const promptText = (text) => new Paragraph({
  spacing: { before: 60, after: 120 },
  children: [new TextRun({ text, italics: true, size: 22, color: "666666" })]
});

const subHeader = (text) => new Paragraph({
  spacing: { before: 160 },
  children: [new TextRun({ text, bold: true, size: 24, color: "002E5D" })]
});

const fieldLabel = (text) => new Paragraph({
  spacing: { before: 120 },
  children: [new TextRun({ text, bold: true, size: 22 })]
});

// Mentoring session ratings table (3 columns: Dimension, TA Rating, Peer Avg)
const createRatingsTable = () => new Table({
  columnWidths: [4000, 2680, 2680],
  rows: [
    new TableRow({ children: [
      headerCell("Dimension", 4000),
      headerCell("TA Rating", 2680),
      headerCell("Peer Avg", 2680)
    ]}),
    new TableRow({ children: [
      dataCell("Impact & Ownership", 4000),
      emptyCell(2680, 60),
      emptyCell(2680, 60)
    ]}),
    new TableRow({ children: [
      dataCell("Teamwork & Collaboration", 4000),
      emptyCell(2680, 60),
      emptyCell(2680, 60)
    ]}),
    new TableRow({ children: [
      dataCell("Presence & Fit", 4000),
      emptyCell(2680, 60),
      emptyCell(2680, 60)
    ]}),
    new TableRow({ children: [
      dataCell("Structure & Approach", 4000),
      emptyCell(2680, 60),
      emptyCell(2680, 60)
    ]}),
    new TableRow({ children: [
      dataCell("Analytical Rigor", 4000),
      emptyCell(2680, 60),
      emptyCell(2680, 60)
    ]}),
    new TableRow({ children: [
      dataCell("Hypothesis-Driven Rec", 4000),
      emptyCell(2680, 60),
      emptyCell(2680, 60)
    ]})
  ]
});

const notesBox = (width = 9360, height = 300) => new Table({
  columnWidths: [width],
  rows: [new TableRow({ children: [emptyCell(width, height)] })]
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal",
        run: { size: 28, bold: true, color: "002E5D", font: "Arial" },
        paragraph: { spacing: { before: 300, after: 120 } } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } } },
    children: [
      // ========== TITLE ==========
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [new TextRun({ text: "STRAT 325: Intro to Management Consulting", bold: true, size: 32, color: "002E5D" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "Goals Worksheet", bold: true, size: 40, color: "002E5D" })]
      }),

      // Student/TA Info
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
              children: [new Paragraph({ children: [
                new TextRun({ text: "Student Name: ", bold: true, size: 22 }),
                new TextRun({ text: "_________________________", size: 22 })
              ]})] }),
            new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
              children: [new Paragraph({ children: [
                new TextRun({ text: "TA Name: ", bold: true, size: 22 }),
                new TextRun({ text: "_________________________", size: 22 })
              ]})] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
              children: [new Paragraph({ spacing: { before: 120 }, children: [
                new TextRun({ text: "Date: ", bold: true, size: 22 }),
                new TextRun({ text: "_________________________", size: 22 })
              ]})] }),
            new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
              children: [new Paragraph({ children: [] })] })
          ]})
        ]
      }),

      // ========== SECTION 1: CAREER DIRECTION ==========
      sectionHeader("1. Career Direction"),
      promptText("What does an ideal first 2-4 years of your career look like, and why?"),
      notesBox(9360, 600),

      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "Summer 2026 Plans:", bold: true, size: 22 })] }),
      promptText("What are your goals for summer 2026? (Internship target firms, industries, or other plans)"),
      notesBox(9360, 400),

      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "Summer 2027 Plans:", bold: true, size: 22 })] }),
      promptText("What are your goals for summer 2027? (Full-time recruiting, graduate school, etc.)"),
      notesBox(9360, 400),

      // ========== SECTION 2: TARGET FIRMS ==========
      sectionHeader("2. Target Firms"),
      promptText("List your top 3 target firms. What differentiates each firm in your mind?"),
      new Table({
        columnWidths: [2200, 4560, 2600],
        rows: [
          new TableRow({ children: [
            headerCell("Firm", 2200),
            headerCell("Why This Firm?", 4560),
            headerCell("Networking Status", 2600)
          ]}),
          new TableRow({ children: [dataCell("1.", 2200), emptyCell(4560, 300), emptyCell(2600, 300)] }),
          new TableRow({ children: [dataCell("2.", 2200), emptyCell(4560, 300), emptyCell(2600, 300)] }),
          new TableRow({ children: [dataCell("3.", 2200), emptyCell(4560, 300), emptyCell(2600, 300)] })
        ]
      }),

      // ========== SECTION 3: SELF-ASSESSMENT ==========
      sectionHeader("3. Self-Assessment"),
      promptText("Rate yourself 1-4 on each dimension. Be honest — this helps you and your TA identify focus areas."),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        children: [
          new TextRun({ text: "Rating Scale: ", bold: true, size: 20 }),
          new TextRun({ text: "1 = Not Yet (significant gaps)  |  2 = Developing (potential but inconsistent)  |  3 = Solid (ready for most interviews)  |  4 = Strong (would stand out)", size: 20, color: "666666" })
        ]
      }),

      subHeader("Behavioral Dimensions"),
      new Table({
        columnWidths: [3000, 5160, 1200],
        rows: [
          new TableRow({ children: [
            headerCell("Dimension", 3000),
            headerCell("What It Means", 5160),
            headerCell("Rating", 1200)
          ]}),
          new TableRow({ children: [
            dataCell("Impact & Ownership", 3000),
            dataCell("Leadership shown, personal actions (\"I\" not \"we\"), quantified results", 5160),
            emptyCell(1200, 100)
          ]}),
          new TableRow({ children: [
            dataCell("Teamwork & Collaboration", 3000),
            dataCell("Working with others, influence, navigating conflict", 5160),
            emptyCell(1200, 100)
          ]}),
          new TableRow({ children: [
            dataCell("Presence & Fit", 3000),
            dataCell("Concise (~2 min), confident, authentic, likable", 5160),
            emptyCell(1200, 100)
          ]})
        ]
      }),

      subHeader("Case Dimensions"),
      new Table({
        columnWidths: [3000, 5160, 1200],
        rows: [
          new TableRow({ children: [
            headerCell("Dimension", 3000),
            headerCell("What It Means", 5160),
            headerCell("Rating", 1200)
          ]}),
          new TableRow({ children: [
            dataCell("Structure & Approach", 3000),
            dataCell("MECE framework, tailored to problem, prioritized", 5160),
            emptyCell(1200, 100)
          ]}),
          new TableRow({ children: [
            dataCell("Analytical Rigor", 3000),
            dataCell("Math setup, accuracy, \"so what\" interpretation", 5160),
            emptyCell(1200, 100)
          ]}),
          new TableRow({ children: [
            dataCell("Hypothesis-Driven Rec", 3000),
            dataCell("Clear POV, insight-led synthesis, practical and actionable", 5160),
            emptyCell(1200, 100)
          ]})
        ]
      }),

      // ========== SECTION 4: DEVELOPMENT FOCUS ==========
      sectionHeader("4. Development Focus"),
      promptText("Based on your self-assessment, identify 2-3 priority skills to develop this semester."),
      new Table({
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          new TableRow({ children: [
            headerCell("Priority Skill", 2340),
            headerCell("Current State", 2340),
            headerCell("Target State (by May)", 2340),
            headerCell("Action Plan", 2340)
          ]}),
          new TableRow({ children: [dataCell("1.", 2340), emptyCell(2340, 400), emptyCell(2340, 400), emptyCell(2340, 400)] }),
          new TableRow({ children: [dataCell("2.", 2340), emptyCell(2340, 400), emptyCell(2340, 400), emptyCell(2340, 400)] }),
          new TableRow({ children: [dataCell("3.", 2340), emptyCell(2340, 400), emptyCell(2340, 400), emptyCell(2340, 400)] })
        ]
      }),

      // ========== SECTION 5: DEFINITION OF SUCCESS ==========
      sectionHeader("5. Definition of Success"),
      promptText("What does \"winning\" look like for you by May 2026? Consider both recruiting outcomes and skill development."),
      notesBox(9360, 700),

      // ========== SECTION 6: TA NOTES ==========
      sectionHeader("6. TA Notes"),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
        children: [new TextRun({ text: "This section is completed by the TA during/after the Goals Chat.", italics: true, size: 20, color: "666666" })]
      }),

      fieldLabel("Key Observations from Conversation:"),
      notesBox(9360, 400),
      fieldLabel("Commitments Made by Student:"),
      notesBox(9360, 300),
      fieldLabel("Flags to Monitor Throughout Semester:"),
      notesBox(9360, 300),
      fieldLabel("How Should I Push This Student? (Preferred Learning Style):"),
      notesBox(9360, 300),

      // ========== PAGE BREAK - MENTORING SESSION 1 ==========
      new Paragraph({ children: [new PageBreak()] }),

      // ========== SECTION 7: MENTORING SESSION 1 ==========
      sectionHeader("7. TA Mentoring Session 1 (Weeks 4-5) — Baseline"),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        shading: { fill: "E3F2FD", type: ShadingType.CLEAR },
        children: [new TextRun({ text: "Purpose: Establish baseline performance data from TA session + early peer practice", italics: true, size: 20, color: "666666" })]
      }),

      new Table({
        columnWidths: [4680, 4680],
        rows: [new TableRow({ children: [
          new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
            children: [new Paragraph({ children: [
              new TextRun({ text: "Date: ", bold: true, size: 22 }),
              new TextRun({ text: "_________________________", size: 22 })
            ]})] }),
          new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
            children: [new Paragraph({ children: [] })] })
        ]})]
      }),

      subHeader("Ratings (1-4 scale)"),
      createRatingsTable(),

      fieldLabel("Key Strengths:"),
      notesBox(9360, 300),
      fieldLabel("Development Priorities:"),
      notesBox(9360, 300),
      fieldLabel("Action Items for Session 2:"),
      notesBox(9360, 300),

      // ========== PAGE BREAK - MENTORING SESSION 2 ==========
      new Paragraph({ children: [new PageBreak()] }),

      // ========== SECTION 8: MENTORING SESSION 2 ==========
      sectionHeader("8. TA Mentoring Session 2 (Weeks 9-10) — Progress Check"),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        shading: { fill: "E3F2FD", type: ShadingType.CLEAR },
        children: [new TextRun({ text: "Purpose: Compare to baseline, calibrate using both TA and peer feedback data", italics: true, size: 20, color: "666666" })]
      }),

      new Table({
        columnWidths: [4680, 4680],
        rows: [new TableRow({ children: [
          new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
            children: [new Paragraph({ children: [
              new TextRun({ text: "Date: ", bold: true, size: 22 }),
              new TextRun({ text: "_________________________", size: 22 })
            ]})] }),
          new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
            children: [new Paragraph({ children: [] })] })
        ]})]
      }),

      subHeader("Ratings (1-4 scale)"),
      createRatingsTable(),

      fieldLabel("Progress Since Session 1:"),
      notesBox(9360, 300),
      fieldLabel("Remaining Gaps:"),
      notesBox(9360, 300),
      fieldLabel("Action Items for Session 3:"),
      notesBox(9360, 300),

      // ========== PAGE BREAK - MENTORING SESSION 3 ==========
      new Paragraph({ children: [new PageBreak()] }),

      // ========== SECTION 9: MENTORING SESSION 3 ==========
      sectionHeader("9. TA Mentoring Session 3 (Week 14) — Final Evaluation"),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        shading: { fill: "E3F2FD", type: ShadingType.CLEAR },
        children: [new TextRun({ text: "Purpose: Assess full-semester growth across all practice interviews", italics: true, size: 20, color: "666666" })]
      }),

      new Table({
        columnWidths: [4680, 4680],
        rows: [new TableRow({ children: [
          new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
            children: [new Paragraph({ children: [
              new TextRun({ text: "Date: ", bold: true, size: 22 }),
              new TextRun({ text: "_________________________", size: 22 })
            ]})] }),
          new TableCell({ borders: noBorders, width: { size: 4680, type: WidthType.DXA },
            children: [new Paragraph({ children: [] })] })
        ]})]
      }),

      subHeader("Ratings (1-4 scale)"),
      createRatingsTable(),

      fieldLabel("Overall Growth Assessment:"),
      notesBox(9360, 300),
      fieldLabel("Interview Readiness:"),
      notesBox(9360, 250),
      fieldLabel("Did student achieve their Definition of Success from Section 5?"),
      new Table({
        columnWidths: [2000, 7360],
        rows: [new TableRow({ children: [
          dataCell("Yes / No / Partial", 2000),
          emptyCell(7360, 200)
        ]})]
      }),
      fieldLabel("Summer Preparation Recommendations:"),
      notesBox(9360, 300)
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/murff/Library/CloudStorage/OneDrive-BrighamYoungUniversity/3. Teaching/management-consulting/resources/goals-worksheet.docx", buffer);
  console.log("Goals Worksheet (with mentoring sessions) created successfully!");
});
