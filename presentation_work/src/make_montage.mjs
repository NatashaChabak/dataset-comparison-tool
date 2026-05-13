import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';
const dir='project_presentation/scratch/previews';
const files=fs.readdirSync(dir).filter(f=>f.endsWith('.png')).sort();
const thumbs=[];
for (const f of files) {
  const input=path.join(dir,f);
  const buf=await sharp(input).resize(384,216).extend({top:24,bottom:8,left:8,right:8,background:'#f3f4f6'}).composite([{input:Buffer.from(`<svg width="384" height="24"><text x="8" y="17" font-size="15" font-family="Arial" fill="#111827">${f}</text></svg>`),top:0,left:8}]).png().toBuffer();
  thumbs.push({input:buf,left:(thumbs.length%2)*400,top:Math.floor(thumbs.length/2)*248});
}
await sharp({create:{width:800,height:Math.ceil(files.length/2)*248,channels:4,background:'#ffffff'}}).composite(thumbs).png().toFile('project_presentation/scratch/montage.png');
console.log('project_presentation/scratch/montage.png');
