// static/js/taean_graph.js

// 지역별 CSV 경로, 방향 레이블·각도
const regionConfigs = {
  '인천': { name: '인천', csv: '/static/finalData/InCheon_05.csv' },
  '여수': { name: '여수', csv: '/static/finalData/Yeosu_05.csv' },
  '태안': { name: '태안', csv: '/static/finalData/Taean_05.csv' },
  '울진': { name: '울진', csv: '/static/finalData/Uljin_05.csv' }
};

const allDirections = [
  'N','NNE','NE','ENE',
  'E','ESE','SE','SSE',
  'S','SSW','SW','WSW',
  'W','WNW','NW','NNW'
];
const allDegrees = allDirections.map((_, i) => i * 22.5);

// CSV에서 숫자 배열 읽어오기
async function loadDirs(csvUrl, colName) {
  const res = await fetch(csvUrl);
  if (!res.ok) throw new Error(`CSV load failed: ${csvUrl}`);
  const text = await res.text();
  const lines = text.trim().split('\n');
  const headers = lines[0].replace(/^\uFEFF/, '').split(',').map(s => s.trim());
  const idx = headers.indexOf(colName);
  if (idx < 0) throw new Error(`컬럼 "${colName}" 없음`);
  return lines.slice(1)
    .map(l => parseFloat(l.split(',')[idx]))
    .filter(v => !isNaN(v));
}

// 폴라 레이아웃 생성
function makePolarLayout(title, placeholderId) {
  const rect = document.getElementById(placeholderId).getBoundingClientRect();
  return {
    title,
    autosize: true,
    width: rect.width,
    height: rect.height,
    margin: { t: 60, r: 40, b: 40, l: 40 },
    polar: {
      bgcolor: 'skyblue',
      angularaxis: {
        direction: 'clockwise',
        rotation: 90,
        tickmode: 'array',
        tickvals: allDegrees,
        ticktext: allDirections,
        tickfont: { size: 17, color: '#222' },
        showline: true, linewidth: 1,
        gridcolor: '#888', gridwidth: 1
      },
      radialaxis: {
        range: [0,1],
        showline: false,
        showticklabels: false,
        gridcolor: '#bbb', gridwidth: 1
      }
    },
    showlegend: false
  };
}

// 애니메이션
function animatePolar(placeholderId, dataArr) {
  const id = `_interval_${placeholderId}`;
  if (window[id]) clearInterval(window[id]);
  let idx = 0;
  window[id] = setInterval(() => {
    if (idx >= dataArr.length) return clearInterval(window[id]);
    const a0 = (dataArr[idx] + 180) % 360;
    const a1 = idx+1 < dataArr.length
      ? (dataArr[idx+1] + 180) % 360
      : null;

    Plotly.restyle(placeholderId, { r:[[0,0.8]], theta:[[a0,a0]] }, [0]);
    Plotly.restyle(placeholderId,
      { r:[[0,0.8]], theta:[[a1!=null? a1:[], a1!=null? a1:[]]] },
      [1]
    );
    idx++;
  }, 1000);
}

// 해향 그리기
async function drawSeaDirPlotly() {
  const placeholderId = 'seaDirChart';
  const chartTitle    = document.getElementById('chartTitle');
  const regionName    = document.body.dataset.region || '태안';
  const cfg           = regionConfigs[regionName];
  if (!cfg) return alert('지원하지 않는 지역입니다!');

  chartTitle.textContent = `🌊 ${cfg.name} 유향`;

  let seaDirs;
  try { seaDirs = await loadDirs(cfg.csv, 'sea_dir_i'); }
  catch(e) { return alert(e.message); }
  if (seaDirs.length === 0) return alert('유향 데이터 없음');

  const arrowSolid = {
    type:'scatterpolar', mode:'lines', r:[0,0.8], theta:[0,0],
    line:{ color:'#1eaf82', width:6 }, hoverinfo:'none', showlegend:false
  };
  const arrowDashed = {
    type:'scatterpolar', mode:'lines', r:[0,0.8], theta:[0,0],
    line:{ color:'#35cfc2', width:4, dash:'dash' },
    hoverinfo:'none', showlegend:false
  };

  Plotly.newPlot(
    placeholderId,
    [arrowSolid, arrowDashed],
    makePolarLayout(`${cfg.name} 유향`, placeholderId),
    { responsive:true }
  );
  animatePolar(placeholderId, seaDirs);
}
window.drawSeaDirPlotly = drawSeaDirPlotly;

// 풍향 그리기
async function drawWindDirPlotly() {
  const placeholderId = 'windDirChart';
  const chartTitle    = document.getElementById('chartTitle');
  const regionName    = document.body.dataset.region || '태안';
  const cfg           = regionConfigs[regionName];
  if (!cfg) return alert('지원하지 않는 지역입니다!');

  chartTitle.textContent = `🌬️ ${cfg.name} 풍향`;

  let windDirs;
  try { windDirs = await loadDirs(cfg.csv, 'wind_dir'); }
  catch(e) { return alert(e.message); }
  if (windDirs.length === 0) return alert('풍향 데이터 없음');

  const arrowSolid = {
    type:'scatterpolar', mode:'lines', r:[0,0.8], theta:[0,0],
    line:{ color:'#0033CC', width:6 }, hoverinfo:'none', showlegend:false
  };
  const arrowDashed = {
    type:'scatterpolar', mode:'lines', r:[0,0.8], theta:[0,0],
    line:{ color:'#3399FF', width:4, dash:'dash' },
    hoverinfo:'none', showlegend:false
  };

  Plotly.newPlot(
    placeholderId,
    [arrowSolid, arrowDashed],
    makePolarLayout(`${cfg.name} 풍향`, placeholderId),
    { responsive:true }
  );
  animatePolar(placeholderId, windDirs);
}
window.drawWindDirPlotly = drawWindDirPlotly;

// 초기 호출 (유향/풍향 숨김 → 해수면 시계열만 보여줌)
function taean_graph() {
  // nothing to do: subpage.js 의 updateChartImg() 가 onload에서 실행됩니다
}
window.taean_graph = taean_graph;
