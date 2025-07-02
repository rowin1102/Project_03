const metrics = ['wind_speed', 'sea_high', 'sea_speed'];
const regionConfigs = [
  { name: '태안', files: ['Taean_05.csv', 'Taean_04.csv'], color: 'red' },
  { name: '인천', files: ['InCheon_04.csv', 'InCheon_04.csv'], color: 'blue' },
  { name: '통영', files: ['TongYeong_04.csv', 'TongYeong_05.csv'], color: 'green' },
  { name: '여수', files: ['Yeosu_04.csv', 'Yeosu_05.csv'], color: 'orange' },
  { name: '울진', files: ['Uljin_04.csv', 'Uljin_05.csv'], color: 'purple' },
];

// 각 그래프 Chart 저장
const charts = {};
const dataBuffers = {};
const indices = {};
const xIndices = {}; // ✅ X축 카운터 관리용

// ✅ 컬럼별 Chart.js 생성
metrics.forEach(metric => {
  const ctx = document.getElementById(
    metric === 'wind_speed' ? 'windChart' :
    metric === 'sea_high' ? 'highChart' : 'speedChart'
  ).getContext('2d');

  charts[metric] = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: regionConfigs.map(region => ({
        label: region.name,
        data: [],
        fill: false,
        tension: 0.4,
        pointRadius: 0.5,
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      parsing: false,
      animation: false,
      scales: {
        x: {
          type: 'linear',
          title: { display: true, text: 'Index' },
        },
        y: { beginAtZero: true }
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            usePointStyle: true,
            pointStyle: 'line',
            boxWidth: 100,
            boxHeight: 7,
          }
        },
        tooltip: { enabled: true }
      },
    }
  });
});

// ✅ 지역 데이터 로딩 + 초기 10개 push
regionConfigs.forEach(region => {
  Promise.all(region.files.map(file =>
    fetch(`/static/finalData/${file}`).then(res => res.text())
  ))
  .then(csvTexts => {
    const allData = csvTexts.flatMap(csvText =>
      Papa.parse(csvText, { header: true, dynamicTyping: true }).data
    );

    metrics.forEach(metric => {
      if (!dataBuffers[metric]) dataBuffers[metric] = {};
      if (!indices[metric]) indices[metric] = {};
      if (!xIndices[metric]) xIndices[metric] = {};

      dataBuffers[metric][region.name] = allData;
      indices[metric][region.name] = 0;

      // ✅ 초기 10개 push
      for (let i = 0; i < 10; i++) {
        const point = allData[i];
        const value = point[metric];
        if (value !== undefined && value !== null && isFinite(value)) {
          charts[metric].data.datasets.find(d => d.label === region.name).data.push({
            x: i,
            y: value
          });
          indices[metric][region.name]++;
        }
      }

      // ✅ 초기 xIndex는 10부터 시작!
      xIndices[metric][region.name] = 10;

      charts[metric].update();
    });
  });
});

// ✅ 이후 실시간: 5초마다 1개 push
setInterval(() => {
  metrics.forEach(metric => {
    regionConfigs.forEach(region => {
      const buffer = dataBuffers[metric][region.name];
      if (!buffer || buffer.length === 0) return;

      const i = indices[metric][region.name];
      const point = buffer[i];
      const value = point[metric];

      if (value !== undefined && value !== null && isFinite(value)) {
        const dataset = charts[metric].data.datasets.find(d => d.label === region.name);
        
        dataset.data.push({
          x: xIndices[metric][region.name], // ✅ X값: 항상 증가하는 카운터 사용
          y: value
        });
        xIndices[metric][region.name]++; // ✅ 다음 push를 위해 +1

        if (dataset.data.length >= 20) {
          dataset.data.shift();
        }
      }

      indices[metric][region.name]++;
      if (indices[metric][region.name] >= buffer.length) {
        indices[metric][region.name] = 0;
      }
    });

    charts[metric].update();
  });
}, 5000);
