import {
  Presentation,
  PresentationFile,
  column,
  row,
  panel,
  text,
  rule,
  fill,
  hug,
  fixed,
  wrap,
  grow,
  drawSlideToCtx,
} from "@oai/artifact-tool";
import { createRequire } from "module";
import fs from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const { Canvas } = require("../../node_modules/@oai/artifact-tool/node_modules/skia-canvas");

const OUT = "project_presentation/output/output.pptx";
const PREVIEW_DIR = "project_presentation/scratch/previews";
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.mkdirSync(PREVIEW_DIR, { recursive: true });

const W = 1920;
const H = 1080;
const COLORS = {
  ink: "#111827",
  muted: "#52616B",
  paper: "#F7F8F4",
  soft: "#E7F0EA",
  line: "#CBD5D1",
  teal: "#0E5C5A",
  teal2: "#4FA39B",
  blue: "#2563EB",
  coral: "#E76F51",
  yellow: "#F3B23C",
  dark: "#0B1F24",
  white: "#FFFFFF",
};

const presentation = Presentation.create({
  slideSize: { width: W, height: H },
});

function t(value, opts = {}) {
  return text(value, {
    width: opts.width ?? fill,
    height: opts.height ?? hug,
    style: {
      fontSize: opts.size ?? 30,
      color: opts.color ?? COLORS.ink,
      bold: opts.bold ?? false,
      italic: opts.italic ?? false,
      fontFace: "Aptos",
      ...opts.style,
    },
    name: opts.name,
  });
}

function bullet(value, color = COLORS.ink) {
  return row(
    { width: fill, height: hug, gap: 16, align: "start" },
    [
      panel({ width: fixed(12), height: fixed(12), fill: COLORS.teal2, borderRadius: "rounded-full" }),
      t(value, { size: 30, color, width: fill }),
    ],
  );
}

function metric(label, value, accent = COLORS.teal) {
  return column(
    { width: fill, height: hug, gap: 8 },
    [
      t(value, { size: 58, bold: true, color: accent }),
      t(label, { size: 21, color: COLORS.muted }),
    ],
  );
}

function featureStep(number, title, detail, accent) {
  return panel(
    { width: grow(1), height: fixed(132), fill: "#F7F8F4", padding: { x: 20, y: 18 } },
    row(
      { width: fill, height: fill, gap: 16 },
      [
        panel(
          { width: fixed(42), height: fixed(42), fill: accent, borderRadius: "rounded-full", padding: { x: 14, y: 9 } },
          t(number, { width: fixed(18), size: 20, bold: true, color: COLORS.white }),
        ),
        column({ width: fill, height: fill, gap: 6, justify: "center" }, [
          t(title, { size: 22, bold: true, color: COLORS.ink }),
          t(detail, { size: 17, color: COLORS.muted, width: fill }),
        ]),
      ],
    ),
  );
}

function timeRow(label, detail, barWidth, color) {
  return row(
    { width: fill, height: fixed(74), gap: 22 },
    [
      t(label, { width: fixed(230), size: 26, bold: true }),
      panel({ width: fixed(barWidth), height: fixed(34), fill: color }),
      t(detail, { width: fixed(600), size: 21, color: COLORS.muted }),
    ],
  );
}

function slideRoot(slide, children, bg = COLORS.paper) {
  slide.compose(
    panel(
      { name: "stage", width: fill, height: fill, fill: bg },
      column({ name: "root", width: fill, height: fill, padding: { x: 96, y: 72 }, gap: 34 }, children),
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function titleSlide(title, subtitle, eyebrow) {
  const slide = presentation.slides.add();
  slideRoot(
    slide,
    [
      row(
        { width: fill, height: grow(1), gap: 64 },
        [
          column(
            { width: grow(1.08), height: fill, gap: 28, justify: "center" },
            [
              t(eyebrow, { size: 24, bold: true, color: COLORS.teal2 }),
              t("Dataset", { size: 78, bold: true, color: COLORS.white, width: fixed(1000), height: fixed(100) }),
              t("Comparison", { size: 78, bold: true, color: COLORS.white, width: fixed(1000), height: fixed(100) }),
              t("Tool", { size: 78, bold: true, color: COLORS.white, width: fixed(1000), height: fixed(100) }),
              rule({ width: fixed(260), stroke: COLORS.yellow, weight: 6 }),
              t(subtitle, { size: 34, color: "#D8ECE8", width: wrap(980) }),
            ],
          ),
          column(
            { width: fixed(520), height: fill, gap: 18, justify: "center" },
            [
              panel({ width: fill, height: fixed(92), fill: "#12323A", padding: { x: 26, y: 22 } }, t("Upload", { size: 30, bold: true, color: COLORS.white })),
              panel({ width: fill, height: fixed(92), fill: "#16434A", padding: { x: 26, y: 22 } }, t("Map fields", { size: 30, bold: true, color: COLORS.white })),
              panel({ width: fill, height: fixed(92), fill: "#1C565A", padding: { x: 26, y: 22 } }, t("Compare with DuckDB", { size: 30, bold: true, color: COLORS.white })),
              panel({ width: fill, height: fixed(92), fill: "#24706C", padding: { x: 26, y: 22 } }, t("Export Excel report", { size: 30, bold: true, color: COLORS.white })),
            ],
          ),
        ],
      ),
      t("ICT project presentation", { size: 20, color: "#A7C7C3" }),
    ],
    COLORS.dark,
  );
}

function contentSlide(title, subtitle, body) {
  const slide = presentation.slides.add();
  slideRoot(slide, [
    column({ width: fill, height: hug, gap: 12 }, [
      t(title, { size: 58, bold: true, color: COLORS.ink }),
      subtitle ? t(subtitle, { size: 25, color: COLORS.muted, width: wrap(1320) }) : null,
    ].filter(Boolean)),
    body,
  ]);
}

titleSlide(
  "Dataset Comparison Tool",
  "A Streamlit application for comparing exported datasets when direct database access is not available.",
  "Python + Streamlit + DuckDB + Parquet",
);

contentSlide(
  "What Is the Project?",
  "The tool helps validate whether two exported datasets contain the same business records and values.",
  row(
    { width: fill, height: grow(1), gap: 64 },
    [
      column({ width: grow(1), height: fill, gap: 28, justify: "center" }, [
        bullet("Upload two datasets in CSV, JSON, or Excel format."),
        bullet("Preview data safely before full comparison."),
        bullet("Map different field names between systems."),
        bullet("Compare records using selected key fields."),
        bullet("Download comparison results as an Excel report."),
      ]),
      panel(
        { width: fixed(560), height: fixed(560), fill: COLORS.soft, padding: { x: 34, y: 34 } },
        column({ width: fill, height: fill, gap: 18, justify: "center" }, [
          metric("Input formats", "CSV / JSON / Excel", COLORS.teal),
          rule({ width: fill, stroke: COLORS.line, weight: 2 }),
          metric("Processing path", "CSV -> Parquet", COLORS.blue),
          rule({ width: fill, stroke: COLORS.line, weight: 2 }),
          metric("Output", "Excel report", COLORS.coral),
        ]),
      ),
    ],
  ),
);

contentSlide(
  "Tools Used",
  "The project used lightweight tools suitable for a small data application and study project.",
  row(
    { width: fill, height: grow(1), gap: 44 },
    [
      column({ width: grow(1), height: fill, gap: 24, justify: "center" }, [
        metric("IDE", "VS Code", COLORS.blue),
        metric("Version control", "Git + GitHub", COLORS.teal),
        metric("Project documentation", "README + Markdown docs", COLORS.coral),
        metric("AI agents", "Codex, supervised use", COLORS.yellow),
      ]),
      column({ width: grow(1), height: fill, gap: 24, justify: "center" }, [
        metric("Frontend", "Streamlit", COLORS.teal),
        metric("Data handling", "Pandas + OpenPyXL", COLORS.blue),
        metric("Large-file engine", "DuckDB + Parquet", COLORS.coral),
      ]),
    ],
  ),
);

contentSlide(
  "Agile Method",
  "I used a simple Kanban-style iterative approach: each feature was built, tested, corrected, and documented.",
  column(
    { width: fill, height: grow(1), gap: 26, justify: "center" },
    [
      row({ width: fill, height: hug, gap: 18 }, [
        featureStep("1", "Input formats", "Added CSV, JSON, and Excel upload.", COLORS.blue),
        featureStep("2", "Settings", "Saved and restored field mappings as JSON.", COLORS.teal),
        featureStep("3", "Comparison", "Added DuckDB and Parquet processing.", COLORS.yellow),
      ]),
      row({ width: fill, height: hug, gap: 18 }, [
        featureStep("4", "Export", "Added Excel download for comparison results.", COLORS.coral),
        featureStep("5", "Fixes", "Corrected errors found during testing.", COLORS.teal2),
        featureStep("6", "Docs", "Updated README, PDF design document, and slides.", COLORS.dark),
      ]),
      t("The method was practical: every increment produced a visible product change that could be tested immediately.", { size: 27, color: COLORS.muted, width: wrap(1360) }),
    ],
  ),
);

contentSlide(
  "Time Usage During the Project",
  "The work was split into short development stages. The bars show relative effort, not exact hours.",
  column(
    { width: fill, height: grow(1), gap: 18, justify: "center" },
    [
      timeRow("Planning", "Project plan, scope, and next steps", 650, COLORS.teal),
      timeRow("MVP UI", "Upload, preview, and key selection", 760, COLORS.blue),
      timeRow("Mapping", "Field mapping and JSON save/restore", 720, COLORS.coral),
      timeRow("Data engine", "DuckDB, Parquet, JSON, and Excel input", 820, COLORS.yellow),
      timeRow("Reporting", "Excel result export and documentation", 600, COLORS.teal2),
    ],
  ),
);

contentSlide(
  "AI Agents Helped under My Supervision",
  "AI assistance was used as a supervised development partner, while I made project decisions and tested the result.",
  row(
    { width: fill, height: grow(1), gap: 54 },
    [
      column({ width: grow(1), height: fill, gap: 26, justify: "center" }, [
        bullet("Helped read project documents and prepare next steps."),
        bullet("Generated code suggestions and implementation drafts."),
        bullet("Helped debug issues and improve the user flow."),
        bullet("Prepared documentation and this presentation draft."),
      ]),
      column({ width: grow(1), height: fill, gap: 26, justify: "center" }, [
        t("My supervision", { size: 44, bold: true, color: COLORS.teal }),
        rule({ width: fixed(180), stroke: COLORS.yellow, weight: 5 }),
        t("I selected the features, checked the behavior, approved changes, tested the Streamlit app, and kept the project aligned with the study goal.", { size: 32, color: COLORS.ink, width: wrap(650) }),
      ]),
    ],
  ),
);

contentSlide(
  "What I Learned",
  "The project connected application development with practical data validation.",
  row(
    { width: fill, height: grow(1), gap: 48 },
    [
      column({ width: grow(1), height: fill, gap: 24, justify: "center" }, [
        metric("Data formats", "CSV, JSON, Excel", COLORS.teal),
        metric("Performance idea", "Parquet for faster processing", COLORS.blue),
        metric("SQL engine", "DuckDB for file-based comparison", COLORS.coral),
      ]),
      column({ width: grow(1), height: fill, gap: 24, justify: "center" }, [
        bullet("Why IDs and codes should stay as text."),
        bullet("How field mapping reduces schema differences."),
        bullet("How small sample data helps prove logic before large files."),
        bullet("How documentation improves project quality."),
      ]),
    ],
  ),
);

contentSlide(
  "Challenges and Solutions",
  "Most challenges came from turning a plan into a real workflow that works with different file types.",
  column(
    { width: fill, height: grow(1), gap: 22, justify: "center" },
    [
      row({ width: fill, height: fixed(120), gap: 24 }, [
        t("Challenge", { width: fixed(330), size: 30, bold: true, color: COLORS.coral }),
        t("Large CSV files could be slow or memory-heavy.", { width: grow(1), size: 30 }),
        t("Solution: preview only first rows, then use DuckDB/Parquet for comparison.", { width: grow(1), size: 30, color: COLORS.teal }),
      ]),
      rule({ width: fill, stroke: COLORS.line, weight: 2 }),
      row({ width: fill, height: fixed(120), gap: 24 }, [
        t("Challenge", { width: fixed(330), size: 30, bold: true, color: COLORS.coral }),
        t("Different systems use different column names.", { width: grow(1), size: 30 }),
        t("Solution: field mapping screen with JSON save and restore.", { width: grow(1), size: 30, color: COLORS.teal }),
      ]),
      rule({ width: fill, stroke: COLORS.line, weight: 2 }),
      row({ width: fill, height: fixed(120), gap: 24 }, [
        t("Challenge", { width: fixed(330), size: 30, bold: true, color: COLORS.coral }),
        t("Users may have JSON or Excel, not only CSV.", { width: grow(1), size: 30 }),
        t("Solution: flatten JSON and read the first Excel sheet automatically.", { width: grow(1), size: 30, color: COLORS.teal }),
      ]),
    ],
  ),
);

contentSlide(
  "Product Demonstration",
  "Suggested live demo: show the full workflow with the sample files in Streamlit.",
  row(
    { width: fill, height: grow(1), gap: 54 },
    [
      column({ width: grow(1), height: fill, gap: 22, justify: "center" }, [
        bullet("Open the app at localhost:8501."),
        bullet("Upload Dataset A and Dataset B."),
        bullet("Select key columns: customer_id and cust_no."),
        bullet("Map fields and mark comparison fields."),
        bullet("Run DuckDB comparison."),
        bullet("Download the Excel report."),
      ]),
      panel(
        { width: fixed(680), height: fixed(520), fill: "#111827", padding: { x: 24, y: 22 } },
        column({ width: fill, height: fill, gap: 14 }, [
          t("Dataset Comparison Tool", { size: 30, bold: true, color: COLORS.white }),
          row({ width: fill, height: fixed(62), gap: 16 }, [
            panel({ width: grow(1), height: fill, fill: "#29313D" }, t("Upload A", { size: 22, color: "#DDE7F0" })),
            panel({ width: grow(1), height: fill, fill: "#29313D" }, t("Upload B", { size: 22, color: "#DDE7F0" })),
          ]),
          panel({ width: fill, height: fixed(104), fill: "#1F2937", padding: { x: 20, y: 14 } }, t("Preview tables + key selection", { size: 24, color: "#DDE7F0" })),
          panel({ width: fill, height: fixed(104), fill: "#23343B", padding: { x: 20, y: 14 } }, t("Field mapping JSON", { size: 24, color: "#DDE7F0" })),
          panel({ width: fill, height: fixed(72), fill: COLORS.teal, padding: { x: 20, y: 16 } }, t("Run comparison  ->  Download Excel", { size: 25, bold: true, color: COLORS.white })),
        ]),
      ),
    ],
  ),
);

contentSlide(
  "Current Status and Next Steps",
  "The project has a working comparison workflow. The next improvements would make it more robust and user-friendly.",
  row(
    { width: fill, height: grow(1), gap: 52 },
    [
      column({ width: grow(1), height: fill, gap: 24, justify: "center" }, [
        t("Done", { size: 44, bold: true, color: COLORS.teal }),
        bullet("CSV, JSON, and Excel upload"),
        bullet("Preview and field mapping"),
        bullet("DuckDB/Parquet comparison"),
        bullet("Excel report download"),
      ]),
      column({ width: grow(1), height: fill, gap: 24, justify: "center" }, [
        t("Next", { size: 44, bold: true, color: COLORS.coral }),
        bullet("Duplicate key detection"),
        bullet("Better charts and visual dashboard"),
        bullet("Choose Excel sheet manually"),
        bullet("More automated tests"),
      ]),
    ],
  ),
);

const pptxBlob = await PresentationFile.exportPptx(presentation);
await pptxBlob.save(OUT);

if (process.env.SKIP_RENDER !== "1") {
  for (let i = 0; i < presentation.slides.items.length; i += 1) {
    const slide = presentation.slides.items[i];
    const canvas = new Canvas(W, H);
    const ctx = canvas.getContext("2d");
    await drawSlideToCtx(slide, presentation, ctx, null, null, null, null, null, null, null, null, { clearBeforeDraw: true });
    await canvas.toFile(path.join(PREVIEW_DIR, `slide-${String(i + 1).padStart(2, "0")}.png`));
  }
}

console.log(JSON.stringify({ pptx: OUT, previews: PREVIEW_DIR, slides: presentation.slides.items.length }, null, 2));
