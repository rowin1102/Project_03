document.addEventListener('DOMContentLoaded', () => {
  const chartPlaceholder = document.getElementById('chartPlaceholder');
  const chartTitle = document.getElementById('chartTitle');
  const windDirBtn = document.getElementById('seaDirBtn');

  // 여러 버튼(해수면, 기압 등) id를 가져온다고 가정 (없으면 querySelectorAll(".column-btn")로 사용)
  const tideBtn      = document.getElementById('tideBtn');
  const pressureBtn  = document.getElementById('pressureBtn');
  const windSpeedBtn = document.getElementById('windSpeedBtn');
  const seaSpeedBtn  = document.getElementById('seaSpeedBtn');
  // 필요하면 seaDirBtn 등도 추가

  // 지역별 config: 이름, csv 경로
  const regionConfigs = {
    '인천':   { name: '인천',   csv: '/static/finalData/InCheon_05.csv' },
    '통영':   { name: '통영',   csv: '/static/finalData/TongYeong_05.csv' },
    '여수':   { name: '여수',   csv: '/static/finalData/Yeosu_05.csv' },
    '울산':   { name: '울산',   csv: '/static/finalData/Ulsan_05.csv' },
    '부산':   { name: '부산',   csv: '/static/finalData/Busan_05.csv' }
  };

  const allDirections = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW'
  ];
  const allDegrees = Array.from({length: 16}, (_, i) => i * 22.5);

  let interval = null;  // 전역으로 유지

  // 🔹 "풍향" 버튼 클릭시
  windDirBtn.addEventListener('click', async () => {
    // 1. 항상 interval 중단(중복방지)
    if (interval) {
      clearInterval(interval);
      interval = null;
    }

    const regionName = document.body.dataset.region || '인천';
    const config = regionConfigs[regionName];
    if (!config) {
      alert('지원하지 않는 지역입니다!');
      return;
    }

    chartTitle.textContent = `🌬️ ${config.name} 유향`;

    // windDirs 새로 읽기
    let windDirs = [];
    try {
      const resp = await fetch(config.csv);
      const text = await resp.text();
      const lines = text.trim().split('\n');
      const headers = lines[0].split(',');
      const dirIdx = headers.indexOf('sea_dir_i');
      if (dirIdx === -1) throw new Error('CSV에 sea_dir 컬럼이 없습니다!');
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(',').map(c => c.trim());
        const dir = parseFloat(cols[dirIdx]);
        if (!isNaN(dir)) windDirs.push(dir);
      }
      if (windDirs.length === 0) throw new Error('유향 데이터 없음');
    } catch (err) {
      alert(err.message);
      return;
    }

    // polar plot 배경
    const layout = {
      title: `${config.name} 유향`,
      width: 600,
      height: 600,
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
      r: [null, null],
      theta: [null, null],
      line: { color: '#0033CC', width: 6, dash: 'solid' },
      marker: { color: '#0033CC' },
      hoverinfo: 'none',
      showlegend: false
    };
    const arrowDashed = {
      type: 'scatterpolar',
      mode: 'lines',
      r: [null, null],
      theta: [null, null],
      line: { color: '#3399FF', width: 4, dash: 'dash' },
      marker: { color: '#3399FF' },
      hoverinfo: 'none',
      showlegend: false
    };

    Plotly.newPlot(chartPlaceholder, [arrowSolid, arrowDashed], layout);

    let idx = 0;

    interval = setInterval(() => {
      if (idx >= windDirs.length) {
        clearInterval(interval);
        interval = null;
        Plotly.restyle(chartPlaceholder, {
          r: [[0, 0.8]],
          theta: [[(windDirs[windDirs.length - 1] + 180) % 360, (windDirs[windDirs.length - 1] + 180) % 360]]
        }, [0]);
        Plotly.restyle(chartPlaceholder, {
          r: [[null, null]],
          theta: [[null, null]]
        }, [1]);
        return;
      }
      // 실선: 현재 방향
      const solidAngle = (windDirs[idx] + 180) % 360;
      Plotly.restyle(chartPlaceholder, {
        r: [[0, 0.8]],
        theta: [[solidAngle, solidAngle]]
      }, [0]);
      // 점선: 다음 방향(없으면 null)
      if (idx + 1 < windDirs.length) {
        const dashedAngle = (windDirs[idx + 1] + 180) % 360;
        Plotly.restyle(chartPlaceholder, {
          r: [[0, 0.8]],
          theta: [[dashedAngle, dashedAngle]]
        }, [1]);
      } else {
        Plotly.restyle(chartPlaceholder, {
          r: [[null, null]],
          theta: [[null, null]]
        }, [1]);
      }
      idx++;
    }, 1000);
  });

  // 🔹 "해수면", "기압", "풍속", "유속" 등 다른 버튼을 클릭하면 interval 종료, plotly 숨김!
  // (버튼 id를 위에서 가져오거나, 아래처럼 querySelectorAll(".column-btn")로 써도 무방)
  [tideBtn, pressureBtn, windSpeedBtn, seaSpeedBtn].forEach(btn => {
    if (btn) {
      btn.addEventListener('click', () => {
        if (interval) {
          clearInterval(interval);
          interval = null;
        }
        chartPlaceholder.style.display = 'none';
        const incheonChart = document.getElementById('incheonChart');
        if (incheonChart) incheonChart.style.display = 'block';
        // Plotly.purge(chartPlaceholder); // 필요시 완전 삭제, (필요없으면 주석처리)
      });
    }
  });
});
