function drawWindDirPlotly(chartStart, hour) {
  const chartPlaceholder = document.getElementById('chartPlaceholder');
  const chartTitle = document.getElementById('chartTitle');
  const regionName = document.body.dataset.region || '태안';

  const regionConfigs = {
      '인천':   { name: '인천',   csv: '/static/finalData/InCheon_05.csv' },
      '여수':   { name: '여수',   csv: '/static/finalData/Yeosu_05.csv' },
      '태안':   { name: '태안',   csv: '/static/finalData/Taean_05.csv' },
      '울진':   { name: '울진',   csv: '/static/finalData/Uljin_05.csv' }
  };

  const config = regionConfigs[regionName];

  const allDirections = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW'
  ];
  const allDegrees = Array.from({length: 16}, (_, i) => i * 22.5);

  (async () => {
    if (!config) {
      alert('지원하지 않는 지역입니다!');
      return;
    }
    chartTitle.textContent = `🌬️ ${config.name} 풍향`;

    const resp = await fetch(config.csv);
    if (!resp.ok) {
      alert(`[ERROR] CSV 파일을 불러올 수 없습니다: ${config.csv}`);
      return;
    }
    const text = await resp.text();
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const dirIdx = headers.indexOf('wind_dir');
    if (dirIdx === -1) {
      alert('CSV에 wind_dir 컬럼이 없습니다!');
      return;
    }
    let windDirs = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',').map(c => c.trim());
      const dir = parseFloat(cols[dirIdx]);
      if (!isNaN(dir)) windDirs.push(dir);
    }
    if (windDirs.length === 0) {
      alert('풍향 데이터 없음');
      return;
    }

    if (window._windInterval) clearInterval(window._windInterval);

    // 컨테이너 크기에 맞춰서 차트 높이 지정!
    const placeholderRect = chartPlaceholder.getBoundingClientRect();
    const plotWidth = placeholderRect.width || 600;
    const plotHeight = placeholderRect.height || 600;

    const layout = {
      title: `${config.name} 풍향`,
      autosize: true,
      width: plotWidth,
      height: plotHeight,
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
          showline: true,
          linewidth: 1,
          showticklabels: true,
          ticks: '',
          gridcolor: '#888',
          gridwidth: 1,
        },
        radialaxis: {
          range: [0, 1],
          showline: false,
          showticklabels: false,
          ticks: '',
          gridcolor: '#bbb',
          gridwidth: 1,
        }
      },
      showlegend: false
    };

    const arrowSolid = {
      type: 'scatterpolar',
      mode: 'lines',
      r: [0, 0.8],
      theta: [0, 0],
      line: { color: '#0033CC', width: 6, dash: 'solid' },
      marker: { color: '#0033CC' },
      hoverinfo: 'none',
      showlegend: false
    };
    const arrowDashed = {
      type: 'scatterpolar',
      mode: 'lines',
      r: [0, 0.8],
      theta: [0, 0],
      line: { color: '#3399FF', width: 4, dash: 'dash' },
      marker: { color: '#3399FF' },
      hoverinfo: 'none',
      showlegend: false
    };

    Plotly.newPlot(chartPlaceholder, [arrowSolid, arrowDashed], layout, {responsive: true});
    Plotly.Plots.resize(chartPlaceholder);

    let idx = 0;
    window._windInterval = setInterval(() => {
      if (idx >= windDirs.length) {
        clearInterval(window._windInterval);
        return;
      }
      const angleSolid = (windDirs[idx] + 180) % 360;
      let angleDashed = null;
      if (idx + 1 < windDirs.length) {
        angleDashed = (windDirs[idx + 1] + 180) % 360;
      }
      Plotly.restyle(chartPlaceholder, { r: [[0, 0.8]], theta: [[angleSolid, angleSolid]] }, [0]);
      if (angleDashed !== null) {
        Plotly.restyle(chartPlaceholder, { r: [[0, 0.8]], theta: [[angleDashed, angleDashed]] }, [1]);
      } else {
        Plotly.restyle(chartPlaceholder, { r: [[null, null]], theta: [[null, null]] }, [1]);
      }
      idx++;
    }, 1000);
  })();
}
window.drawWindDirPlotly = drawWindDirPlotly;
