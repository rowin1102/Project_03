document.addEventListener('DOMContentLoaded', () => {
  const chartPlaceholder = document.getElementById('chartPlaceholder');
  const chartTitle = document.getElementById('chartTitle');
  const windDirBtn = document.getElementById('windDirBtn');

  const regionConfigs = {
    '인천': {
      name: '인천',
      files: ['../finalData/InCheon_05.csv'],
      roseColor: '#7EC8E3',
      solidColor: '#0033CC',
      dashedColor: '#3399FF'
    }
  };

  const regionName = document.body.dataset.region || '인천';
  const regionConfig = regionConfigs[regionName];
  if (!regionConfig) {
    console.error('잘못된 지역 설정!');
    return;
  }

  // 16방위
  const allDirections = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW'
  ];
  const allDegrees = Array.from({length: 16}, (_, i) => i * 22.5);

  function degreeToDirection(degree) {
    const idx = Math.floor(((degree + 11.25) % 360) / 22.5);
    return allDirections[idx];
  }

  windDirBtn.addEventListener('click', async () => {
    const columnBtns = document.querySelectorAll('.columns-grid .column-btn');
    columnBtns.forEach(b => b.classList.remove('active'));
    windDirBtn.classList.add('active');

    chartTitle.textContent = `🌬️ ${regionConfig.name} 풍향`;

    const windDirs = [];
    const windDirections = [];

    for (const file of regionConfig.files) {
      const response = await fetch(`/static/csv/${file}`);
      const csvText = await response.text();

      const lines = csvText.trim().split('\n');
      const headers = lines[0].split(',').map(h => h.trim());

      const dirIdx = headers.indexOf('wind_dir');
      if (dirIdx === -1) {
        console.error('CSV에 wind_dir 컬럼이 없습니다!');
        console.log('헤더:', headers);
        return;
      }

      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(',').map(c => c.trim());
        const dir = parseFloat(cols[dirIdx]);
        if (!isNaN(dir)) {
          windDirs.push(dir);
          windDirections.push(degreeToDirection(dir));
        }
      }
    }

    if (windDirs.length < 2) {
      alert('데이터가 부족합니다.');
      return;
    }

    // 풍장미도용 bins
    const binsMap = new Map();
    windDirections.forEach(dirText => {
      binsMap.set(dirText, (binsMap.get(dirText) || 0) + 1);
    });
    const bins = allDirections.map(dir => binsMap.get(dir) || 0);

    // 장미도
    const roseTrace = {
      type: 'barpolar',
      r: bins,
      theta: allDirections,
      width: 360 / 16,
      marker: { color: regionConfig.roseColor, opacity: 0.6 },
      name: '풍향장미도'
    };

    // 화살표 및 텍스트 trace 생성 함수
    function getArrowTraces(idx, style) {
      if (idx >= windDirs.length) return [];
      const theta = (windDirs[idx] + 180) % 360; // 실제로 바람이 부는 방향
      const dirText = degreeToDirection(windDirs[idx]);
      // 화살표
      const arrowTrace = {
        type: 'scatterpolar',
        mode: 'lines+markers',
        r: [0, 30],
        theta: [theta, theta],
        name: style.name,
        line: { dash: style.dash, color: style.color, width: style.width },
        marker: { color: style.color },
        showlegend: true
      };
      // 화살표 끝 텍스트
      const textTrace = {
        type: 'scatterpolar',
        mode: 'text',
        r: [32],
        theta: [theta],
        text: [dirText],
        textfont: { size: 22, color: style.color, weight: 'bold' },
        showlegend: false,
        hoverinfo: 'skip'
      };
      return [arrowTrace, textTrace];
    }

    // 초기 표시
    let currentIndex = 0;
    let traces = [
      roseTrace,
      ...getArrowTraces(0, {name: '실선 화살표', dash: 'solid', color: regionConfig.solidColor, width: 4})
    ];
    if (windDirs.length > 1) {
      traces.push(...getArrowTraces(1, {name: '점선 화살표', dash: 'dash', color: regionConfig.dashedColor, width: 3}));
    }

    const layout = {
      title: `${regionConfig.name} 풍향`,
      width: 800,
      height: 800,
      polar: {
        bgcolor: 'skyblue',
        angularaxis: {
          direction: 'clockwise',
          rotation: 90,
          tickmode: 'array',
          tickvals: allDegrees,
          ticktext: allDirections,
          tickfont: { size: 18, color: 'black' },
          ticklen: 12
        },
        radialaxis: { visible: true, range: [0, 45], tickfont: { size: 14 } }
      },
      showlegend: true,
      legend: { orientation: "h", x: 0.5, xanchor: "center", y: 1.07 }
    };

    Plotly.newPlot(chartPlaceholder, traces, layout);

    // 애니메이션
    const interval = setInterval(() => {
      if (currentIndex + 1 >= windDirs.length) {
        clearInterval(interval);
        console.log('애니메이션 종료');
        return;
      }
      currentIndex++;
      let newTraces = [
        roseTrace,
        ...getArrowTraces(currentIndex, {name: '실선 화살표', dash: 'solid', color: regionConfig.solidColor, width: 4})
      ];
      if (currentIndex + 1 < windDirs.length) {
        newTraces.push(...getArrowTraces(currentIndex + 1, {name: '점선 화살표', dash: 'dash', color: regionConfig.dashedColor, width: 3}));
      }
      Plotly.react(chartPlaceholder, newTraces, layout);
    }, 1000); // 실제 10분: 600000
  });
});
