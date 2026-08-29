const sharp = require('sharp');

async function createFunnel() {
  // Funnel SVG - wide at top (MCA), narrow at bottom (STRAT 325)
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500">
    <defs>
      <linearGradient id="funnelGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:#002E5D"/>
        <stop offset="100%" style="stop-color:#C4A44A"/>
      </linearGradient>
    </defs>
    <!-- Funnel shape: wide top narrowing to bottom -->
    <path d="M 80,0 L 720,0 L 720,60 C 720,60 580,200 520,320 L 520,440 L 520,500 L 280,500 L 280,440 L 280,320 C 220,200 80,60 80,60 Z"
          fill="url(#funnelGrad)" opacity="0.9"/>

    <!-- Horizontal divider line in the funnel -->
    <line x1="200" y1="180" x2="600" y2="180" stroke="#ffffff" stroke-width="2" stroke-dasharray="8,4" opacity="0.6"/>

    <!-- Top section label -->
    <text x="400" y="50" text-anchor="middle" font-family="Arial" font-size="28" font-weight="bold" fill="#ffffff">MCA</text>
    <text x="400" y="85" text-anchor="middle" font-family="Arial" font-size="16" fill="#ffffff" opacity="0.9">Fall Semester</text>

    <!-- Number in top section -->
    <text x="400" y="140" text-anchor="middle" font-family="Arial" font-size="42" font-weight="bold" fill="#ffffff">60-100</text>
    <text x="400" y="165" text-anchor="middle" font-family="Arial" font-size="14" fill="#ffffff" opacity="0.8">students across campus</text>

    <!-- Filter zone -->
    <text x="400" y="215" text-anchor="middle" font-family="Arial" font-size="13" fill="#ffffff" opacity="0.7">Presidency filters who is ready</text>

    <!-- Arrow indicators on sides -->
    <polygon points="160,100 140,120 160,140" fill="#ffffff" opacity="0.3"/>
    <polygon points="640,100 660,120 640,140" fill="#ffffff" opacity="0.3"/>
    <polygon points="260,250 240,270 260,290" fill="#ffffff" opacity="0.3"/>
    <polygon points="540,250 560,270 540,290" fill="#ffffff" opacity="0.3"/>

    <!-- Bottom section label -->
    <text x="400" y="350" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="#ffffff">STRAT 325</text>
    <text x="400" y="380" text-anchor="middle" font-family="Arial" font-size="14" fill="#ffffff" opacity="0.9">Winter Semester</text>

    <!-- Bottom details -->
    <text x="400" y="420" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="#ffffff">3 Credits  |  2x/week</text>
    <text x="400" y="450" text-anchor="middle" font-family="Arial" font-size="13" fill="#ffffff" opacity="0.8">Serious candidates targeting MBB+</text>
    <text x="400" y="475" text-anchor="middle" font-family="Arial" font-size="13" fill="#ffffff" opacity="0.8">Interview prep + live consulting projects</text>
  </svg>`;

  await sharp(Buffer.from(svg)).png().toFile('funnel.png');
  console.log('Created funnel.png');
}

createFunnel().catch(console.error);
