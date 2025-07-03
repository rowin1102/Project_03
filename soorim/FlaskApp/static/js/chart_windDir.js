document.addEventListener('DOMContentLoaded', () => {
  const chartPlaceholder = document.getElementById('chartPlaceholder');
  const chartTitle = document.getElementById('chartTitle');
  const windDirBtn = document.getElementById('windDirBtn');

  const regionConfigs = {
    '인천': { name: '인천', files: ['../finalData/InCheon_05.csv'], color: 'blue' },
  };

  const regionName = document.body.dataset.region || '인천';
  const regionConfig = regionConfigs[regionName];
  if (!regionConfig) {
    console.error('잘못된 지역 설정!');
    return;
  }

  windDirBtn.addEventListener('click', async () => {
    const columnBtns = document.querySelectorAll('.columns-grid .column-btn');
    columnBtns.forEach(b => b.classList.remove('active'));
    windDirBtn.classList.add('active');

    chartTitle.textContent = `🌬️ ${regionConfig.name} 풍향`;

    const windDirs = [];

    for (const file of regionConfig.files) {
      const response = await fetch(`/static/csv/${file}`);
      const csvText = await response.text();

      const lines = csvText.trim().split('\n');
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase());

      const dirIdx = headers.findIndex(h => h.includes('wind'));
      if (dirIdx === -1) {
        console.error('CSV에 wind_dir 컬럼이 없습니다.');
        return;
      }

      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(',').map(c => c.trim());
        const dir = parseInt(cols[dirIdx], 10); // int로 읽기
        if (!isNaN(dir)) windDirs.push(dir);
      }
    }

    if (windDirs.length < 2) {
      alert('데이터가 부족합니다.');
      return;
    }

    // ✅ 풍향 장미도 bins
    const bins = Array(16).fill(0);
    windDirs.forEach(dir => {
      const idx = Math.floor((dir % 360) / 22.5) % 16;
      bins[idx]++;
    });

    const directions = [
      'N', 'NNE', 'NE', 'ENE',
      'E', 'ESE', 'SE', 'SSE',
      'S', 'SSW', 'SW', 'WSW',
      'W', 'WNW', 'NW', 'NNW'
    ];

    const roseTrace = {
      type: 'barpolar',
      r: bins,
      theta: directions,
      width: 360 / 16,
      marker: { color: regionConfig.color, opacity: 0.5 },
      name: '풍향장미도'
    };

    // ✅ 실선 화살표 + 점선 화살표
    let index = 1;

    let solidArrow = {
      type: 'scatterpolar',
      mode: 'lines+markers',
      r: [0, 30],
      theta: [windDirs[0], windDirs[0]],
      name: '실선 화살표',
      line: { dash: 'solid', color: regionConfig.color, width: 3 }
    };

    let dashedArrow = {
      type: 'scatterpolar',
      mode: 'lines+markers',
      r: [0, 30],
      theta: [windDirs[1], windDirs[1]],
      name: '점선 화살표',
      line: { dash: 'dash', color: regionConfig.color, width: 2 }
    };

    const layout = {
      title: `${regionConfig.name} 풍향`,
      width: 800,
      height: 800,
      polar: {
        angularaxis: { direction: 'clockwise', rotation: 90 },
        radialaxis: { visible: true, range: [0, 40] }
      }
    };

    Plotly.newPlot(chartPlaceholder, [roseTrace, solidArrow, dashedArrow], layout);

    index++;

    const interval = setInterval(() => {
      if (index >= windDirs.length) {
        clearInterval(interval);
        console.log('애니메이션 종료');
        return;
      }

      solidArrow = {
        ...dashedArrow,
        name: '실선 화살표',
        line: { dash: 'solid', color: regionConfig.color, width: 3 }
      };

      dashedArrow = {
        type: 'scatterpolar',
        mode: 'lines+markers',
        r: [0, 30],
        theta: [windDirs[index], windDirs[index]],
        name: '점선 화살표',
        line: { dash: 'dash', color: regionConfig.color, width: 2 }
      };

      Plotly.react(chartPlaceholder, [roseTrace, solidArrow, dashedArrow], layout);
      index++;
    }, 1000); // 실제는 10분이면 600000으로!
  });
});
