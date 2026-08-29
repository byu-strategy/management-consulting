const pptxgen = require('pptxgenjs');
const html2pptx = require('/Users/murff/.claude/skills/pptx/scripts/html2pptx');
const path = require('path');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Scott Murff';
    pptx.title = 'MCA + STRAT 325 Pipeline';

    // Slide 1: Pipeline diagram
    await html2pptx(path.join(__dirname, 'slide1.html'), pptx);

    // Slide 2: Original whiteboard photo
    const slide2 = pptx.addSlide();

    // White background
    slide2.background = { color: 'FFFFFF' };

    // Title
    slide2.addText('Original Whiteboard Sketch', {
        x: 0.5, y: 0.2, w: 9, h: 0.5,
        fontSize: 20, color: '002E5D', bold: true,
        fontFace: 'Arial'
    });

    // Image - 5712x4284 -> aspect ratio = 1.333
    const imgW = 8.0;
    const imgH = imgW / (5712 / 4284);
    const imgX = (10 - imgW) / 2;

    slide2.addImage({
        path: path.resolve('/Users/murff/Library/CloudStorage/OneDrive-BrighamYoungUniversity/3. Teaching/management-consulting/IMG_8556.jpg'),
        x: imgX, y: 0.85, w: imgW, h: imgH
    });

    const outPath = path.resolve('/Users/murff/Library/CloudStorage/OneDrive-BrighamYoungUniversity/3. Teaching/management-consulting/mca-strat325-pipeline.pptx');
    await pptx.writeFile({ fileName: outPath });
    console.log('Created: ' + outPath);
}

createPresentation().catch(console.error);
