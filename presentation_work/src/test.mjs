import { Presentation, PresentationFile, column, text, panel, fill, hug, wrap, fixed } from '@oai/artifact-tool';
const p=Presentation.create({slideSize:{width:1920,height:1080}});
const s=p.slides.add();
s.compose(column({name:'root', width:fill, height:fill, padding:{x:100,y:80}, gap:30},[
  text('Test title',{name:'t',width:fill,height:hug,style:{fontSize:72,bold:true,color:'#111827'}}),
  panel({name:'p', width:fixed(400), height:fixed(200), fill:'#E0F2FE', padding:{x:24,y:24}}, text('Panel text',{width:fill,height:hug,style:{fontSize:28,color:'#0F172A'}}))
]),{frame:{left:0,top:0,width:1920,height:1080},baseUnit:8});
const blob=await PresentationFile.exportPptx(p); await blob.save('presentation_work/output/test.pptx');
