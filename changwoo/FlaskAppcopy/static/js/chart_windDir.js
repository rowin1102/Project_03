// // document.addEventListener('DOMContentLoaded', () => {
// //   const chartPlaceholder = document.getElementById('chartPlaceholder');
// //   const chartTitle = document.getElementById('chartTitle');
// //   const windDirBtn = document.getElementById('windDirBtn');

// window.addEventListener('load', () => {
//   const chartPlaceholder = document.getElementById('chartPlaceholder');
//   const chartTitle = document.getElementById('chartTitle');
//   const windDirBtn = document.getElementById('windDirBtn');

//   if (!windDirBtn) {
//     console.error('[ERROR] windDirBtn 요소를 찾을 수 없음!');
//     return;
//   }
//   console.log('[DEBUG] windDirBtn =', windDirBtn);

//   windDirBtn.addEventListener('click', async () => {
//     console.log('[DEBUG] 풍향 버튼 클릭됨');


//   // 지역별 config: 이름, csv 경로
//   const regionConfigs = {
//     '인천':   { name: '인천',   csv: './finalData/InCheon_05.csv' },
//     '목포':   { name: '목포',   csv: './finalData/Mokpo_05.csv' },
//     '여수':   { name: '여수',   csv: './finalData/Yeosu_05.csv' },
//     '울산':   { name: '울산',   csv: './finalData/Ulsan_05.csv' },
//     '태안':   { name: '태안',   csv: './finalData/Taean_05.csv' } 
//     // 필요하면 더 추가
//   };

//   // 16방위 ticktext와 각도
//   const allDirections = [
//     'N', 'NNE', 'NE', 'ENE',
//     'E', 'ESE', 'SE', 'SSE',
//     'S', 'SSW', 'SW', 'WSW',
//     'W', 'WNW', 'NW', 'NNW'
//   ];
//   const allDegrees = Array.from({length: 16}, (_, i) => i * 22.5);

//   let interval;
//   let windDirs = [];

  
//   windDirBtn.addEventListener('click', async () => {
//      console.log('[DEBUG] 풍향 버튼 클릭됨'); // ✅ 여기에 추가
//     clearInterval(interval);

//     // 현재 지역 읽기
//     const regionName = document.body.dataset.region || '태안';
//     const config = regionConfigs[regionName];
//     if (!config) {
//       alert('지원하지 않는 지역입니다!');
//       return;
//     }

//     chartTitle.textContent = `🌬️ ${config.name} 풍향`;

//     // windDirs 초기화(다시 지역 버튼 클릭시 새로 fetch)
//     windDirs = [];

//     // CSV 데이터 fetch & windDirs 추출
//     const resp = await fetch(config.csv);
//     const text = await resp.text();
//     const lines = text.trim().split('\n');
//     const headers = lines[0].split(',');
//     const dirIdx = headers.indexOf('wind_dir');
//     if (dirIdx === -1) {
//       alert('CSV에 wind_dir 컬럼이 없습니다!');
//       return;
//     }
//     for (let i = 1; i < lines.length; i++) {
//       const cols = lines[i].split(',').map(c => c.trim());
//       const dir = parseFloat(cols[dirIdx]);
//       if (!isNaN(dir)) windDirs.push(dir);
//     }
//     if (windDirs.length === 0) {
//       alert('풍향 데이터 없음');
//       return;
//     }

//     // (1) 배경 고정(나침반, skyblue)
//     const layout = {
//       title: `${config.name} 풍향`,
//       width: 600,
//       height: 600,
//       margin: { t: 60, r: 40, b: 40, l: 40 },
//       polar: {
//         bgcolor: 'skyblue',
//         angularaxis: {
//           direction: 'clockwise',
//           rotation: 90,
//           tickmode: 'array',
//           tickvals: allDegrees,
//           ticktext: allDirections,
//           tickfont: { size: 17, color: '#222' },
//           showline: true,
//           linewidth: 1,
//           showticklabels: true,
//           ticks: '',
//           gridcolor: '#888',
//           gridwidth: 1,
//         },
//         radialaxis: {
//           range: [0, 1],
//           showline: false,
//           showticklabels: false,
//           ticks: '',
//           gridcolor: '#bbb',
//           gridwidth: 1,
//         }
//       },
//       showlegend: false
//     };

//     // (2) 최초: 화살표 2개(실선, 점선) 빈 상태
//     const arrowSolid = {
//       type: 'scatterpolar',
//       mode: 'lines',
//       r: [0, 0.8],
//       theta: [0, 0],
//       line: { color: '#0033CC', width: 6, dash: 'solid' },
//       marker: { color: '#0033CC' },
//       hoverinfo: 'none',
//       showlegend: false
//     };
//     const arrowDashed = {
//       type: 'scatterpolar',
//       mode: 'lines',
//       r: [0, 0.8],
//       theta: [0, 0],
//       line: { color: '#3399FF', width: 4, dash: 'dash' },
//       marker: { color: '#3399FF' },
//       hoverinfo: 'none',
//       showlegend: false
//     };

//     Plotly.newPlot(chartPlaceholder, [arrowSolid, arrowDashed], layout);

//     let idx = 0;

//     interval = setInterval(() => {
//       if (idx >= windDirs.length) {
//         clearInterval(interval);
//         return;
//       }
//       // 실선 화살표(현재 데이터)
//       const angleSolid = (windDirs[idx] + 180) % 360;
//       let angleDashed = null;
//       if (idx + 1 < windDirs.length) {
//         angleDashed = (windDirs[idx + 1] + 180) % 360;
//       }

//       // 실선/점선 화살표만 restyle!
//       Plotly.restyle(chartPlaceholder, {
//         r: [[0, 0.8]],
//         theta: [[angleSolid, angleSolid]]
//       }, [0]);
//       if (angleDashed !== null) {
//         Plotly.restyle(chartPlaceholder, {
//           r: [[0, 0.8]],
//           theta: [[angleDashed, angleDashed]]
//         }, [1]);
//       } else {
//         // 다음 데이터 없으면 점선 없앰
//         Plotly.restyle(chartPlaceholder, {
//           r: [[null, null]],
//           theta: [[null, null]]
//         }, [1]);
//       }
//       idx++;
//     }, 1000);
//   });
// });
window.addEventListener('load', () => {
  const chartPlaceholder = document.getElementById('chartPlaceholder');
  const chartTitle = document.getElementById('chartTitle');
  const windDirBtn = document.getElementById('windDirBtn');
  
  const regionName = document.body.dataset.region || '태안';
  if (!windDirBtn) {
    console.error('[ERROR] windDirBtn 요소를 찾을 수 없음!');
    return;
  }
  console.log('[DEBUG] regionName =', regionName);

  console.log('[DEBUG] windDirBtn =', windDirBtn);

  // 지역별 config: 이름, csv 경로
  const regionConfigs = {
    '인천':   { name: '인천',   csv: './static/finalData/InCheon_05.csv' },
    '목포':   { name: '목포',   csv: './static/finalData/Mokpo_05.csv' },
    '여수':   { name: '여수',   csv: './static/finalData/Yeosu_05.csv' },
    '울산':   { name: '울산',   csv: './static/finalData/Ulsan_05.csv' },
    '태안':   { name: '태안',   csv: '/static/finalData/Taean_05.csv' } 
  };

  const allDirections = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW'
  ];
  const allDegrees = Array.from({length: 16}, (_, i) => i * 22.5);

  let interval;
  let windDirs = [];

    windDirBtn.addEventListener('click', async () => {
    console.log('[DEBUG] 풍향 버튼 클릭됨 ✅');

    clearInterval(interval);
    windDirs = [];

    const regionName = document.body.dataset.region || '태안';
    const config = regionConfigs[regionName];
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
    const headers = lines[0].split('\t').map(h => h.trim());
    const dirIdx = headers.indexOf('wind_dir');
    if (dirIdx === -1) {
      alert('CSV에 wind_dir 컬럼이 없습니다!');
      return;
    }
    console.log('[DEBUG] headers =', headers);
    console.log('[DEBUG] wind_dir index =', dirIdx);

    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split('\t').map(c => c.trim());
      const dir = parseFloat(cols[dirIdx]);
      if (!isNaN(dir)) windDirs.push(dir);
    }

    if (windDirs.length === 0) {
      alert('풍향 데이터 없음');
      return;
    }

    const layout = {
      title: `${config.name} 풍향`,
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

    Plotly.newPlot(chartPlaceholder, [arrowSolid, arrowDashed], layout);
    Plotly.Plots.resize(chartPlaceholder);
    let idx = 0;
    interval = setInterval(() => {
      if (idx >= windDirs.length) {
        clearInterval(interval);
        return;
      }

      const angleSolid = (windDirs[idx] + 180) % 360;
      let angleDashed = null;
      if (idx + 1 < windDirs.length) {
        angleDashed = (windDirs[idx + 1] + 180) % 360;
      }

      Plotly.restyle(chartPlaceholder, {
        r: [[0, 0.8]],
        theta: [[angleSolid, angleSolid]]
      }, [0]);

      if (angleDashed !== null) {
        Plotly.restyle(chartPlaceholder, {
          r: [[0, 0.8]],
          theta: [[angleDashed, angleDashed]]
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
});
