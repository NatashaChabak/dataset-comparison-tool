import fs from "node:fs";
import JSZip from "jszip";

const pptxPath = "project_presentation/output/output.pptx";
const data = fs.readFileSync(pptxPath);
const zip = await JSZip.loadAsync(data);
const names = Object.keys(zip.files);
const slideNames = names
  .filter((name) => /^ppt\/slides\/slide\d+\.xml$/.test(name))
  .sort((a, b) => Number(a.match(/slide(\d+)/)[1]) - Number(b.match(/slide(\d+)/)[1]));
const mediaNames = names.filter((name) => name.startsWith("ppt/media/"));
const placeholderPattern = /\b(Slide Number|Click to add|Lorem ipsum|Replace with|TODO|TBD)\b/i;
const placeholders = [];

for (const slideName of slideNames) {
  const xml = await zip.files[slideName].async("string");
  if (placeholderPattern.test(xml)) {
    placeholders.push(slideName);
  }
}

const result = {
  pptxPath,
  slideCount: slideNames.length,
  mediaCount: mediaNames.length,
  placeholders,
  ok: slideNames.length === 10 && placeholders.length === 0,
};

fs.writeFileSync(
  "project_presentation/scratch/package-check.json",
  JSON.stringify(result, null, 2),
);

if (!result.ok) {
  console.error(JSON.stringify(result, null, 2));
  process.exit(1);
}

console.log(JSON.stringify(result, null, 2));
