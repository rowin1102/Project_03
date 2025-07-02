const metrics = ['wind_speed', 'sea_speed'];
const regionConfigs = [
  { name: '태안', files: ['Taean_05.csv', 'Taean_04.csv'], color: 'red' },
  { name: '인천', files: ['InCheon_04.csv', 'InCheon_04.csv'], color: 'blue' },
  { name: '통영', files: ['TongYeong_04.csv', 'TongYeong_05.csv'], color: 'green' },
  { name: '여수', files: ['Yeosu_04.csv', 'Yeosu_05.csv'], color: 'orange' },
  { name: '울진', files: ['Uljin_04.csv', 'Uljin_05.csv'], color: 'purple' },
];

// ✅ 저장소
const charts = {};
const dataBuffers = {};
const indices = {};
const timeIndices = {};       // 초기: -50 ~ -5
const nextTimeIndices = {};   // 이후: 0부터 +5씩

// ✅ sea_high 전용
const seaHighThresholds = {
  low: v => v < 70,
  mid: v => v >= 70 && v <= 100,
  high: v => v > 100
};
const seaHighCurrent = {};
const seaHighBuffer = {};
const seaHighIndex = {};
regionConfigs.forEach(region => {
  seaHighCurrent[region.name] = [0, 0, 0];
});

// ✅ wind_speed & sea_speed 꺾은선
metrics.forEach(metric => {
  const ctx = document.getElementById(
    metric === 'wind_speed' ? 'windChart' : 'speedChart'
  ).getContext('2d');

  charts[metric] = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: regionConfigs.map(region => ({
        label: region.name,
        data: [],
        fill: false,
        tension: 0.4,
        pointRadius: 2,

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
          title: { display: true, text: 'Time (s)' },
          grid: { display: true }
        },
        y: {
          beginAtZero: true,
          grid: { display: true }
        }
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            usePointStyle: true,
            pointStyle: 'line',
            boxWidth: 40,
            boxHeight: 4
          }
        },
        tooltip: { enabled: true }
      }
    }
  });
});

// ✅ sea_high 수평 막대
const ctx = document.getElementById('highBarChart').getContext('2d');
const seaHighChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: regionConfigs.map(r => r.name),
    datasets: [
      { label: '낮음(0~70)', data: [], backgroundColor: '#F44336' },
      { label: '보통(70~100)', data: [], backgroundColor: '#FFC107' },
      { label: '높음(100~)', data: [], backgroundColor: '#4CAF50' },
    ]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        beginAtZero: true,
        title: { display: true, text: '파고(cm)' }
      },
      y: {
        title: { display: true, text: '지역' }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'rect'
        }
      }
    }
  }
});

// ✅ 데이터 로딩
regionConfigs.forEach(region => {
  Promise.all(region.files.map(file =>
    fetch(`/static/finalData/${file}`).then(res => res.text())
  ))
  .then(csvTexts => {
    const allData = csvTexts.flatMap(csvText =>
      Papa.parse(csvText, { header: true, dynamicTyping: true }).data
    );

    // ✔ 꺾은선 초기 10개 (X: -50 ~ -5)
    metrics.forEach(metric => {
      if (!dataBuffers[metric]) dataBuffers[metric] = {};
      if (!indices[metric]) indices[metric] = {};
      if (!timeIndices[metric]) timeIndices[metric] = {};
      if (!nextTimeIndices[metric]) nextTimeIndices[metric] = {};

      dataBuffers[metric][region.name] = allData;
      indices[metric][region.name] = 0;
      timeIndices[metric][region.name] = -50;

      for (let i = 0; i < 10; i++) {
        const value = allData[i][metric];
        if (value !== undefined && isFinite(value)) {
          charts[metric].data.datasets.find(d => d.label === region.name).data.push({
            x: timeIndices[metric][region.name],
            y: value
          });
          indices[metric][region.name]++;
          timeIndices[metric][region.name] += 5;
        }
      }

      nextTimeIndices[metric][region.name] = 0; // ✔ 이후 0부터 시작
      charts[metric].update();
    });

    // ✔ sea_high 버퍼 + 시작 시 1개 반영
    seaHighBuffer[region.name] = allData;
    seaHighIndex[region.name] = 0;

    const v = allData[0]?.sea_high;
    seaHighCurrent[region.name] = [0, 0, 0];
    if (v !== undefined && isFinite(v)) {
      if (seaHighThresholds.low(v)) seaHighCurrent[region.name][0] = v;
      else if (seaHighThresholds.mid(v)) seaHighCurrent[region.name][1] = v;
      else if (seaHighThresholds.high(v)) seaHighCurrent[region.name][2] = v;
    }
    seaHighIndex[region.name] = 1;
    updateSeaHighChart();
  });
});

// ✅ 5초마다
setInterval(() => {
  metrics.forEach(metric => {
    regionConfigs.forEach(region => {
      const buffer = dataBuffers[metric][region.name];
      if (!buffer || buffer.length === 0) return;

      const i = indices[metric][region.name];
      const value = buffer[i][metric];
      if (value !== undefined && isFinite(value)) {
        const dataset = charts[metric].data.datasets.find(d => d.label === region.name);
        dataset.data.push({
          x: nextTimeIndices[metric][region.name],
          y: value
        });
        nextTimeIndices[metric][region.name] += 5; // ✔ 5초 증가
        if (dataset.data.length > 20) dataset.data.shift();
      }

      indices[metric][region.name]++;
      if (indices[metric][region.name] >= buffer.length) indices[metric][region.name] = 0;
    });
    charts[metric].update();
  });

  // ✔ sea_high
  regionConfigs.forEach(region => {
    const buffer = seaHighBuffer[region.name];
    if (!buffer || buffer.length === 0) return;

    const i = seaHighIndex[region.name];
    const v = buffer[i]?.sea_high;

    seaHighCurrent[region.name] = [0, 0, 0];
    if (v !== undefined && isFinite(v)) {
      if (seaHighThresholds.low(v)) seaHighCurrent[region.name][0] = v;
      else if (seaHighThresholds.mid(v)) seaHighCurrent[region.name][1] = v;
      else if (seaHighThresholds.high(v)) seaHighCurrent[region.name][2] = v;
    }

    seaHighIndex[region.name]++;
    if (seaHighIndex[region.name] >= buffer.length) seaHighIndex[region.name] = 0;
  });

  updateSeaHighChart();
}, 5000);

function updateSeaHighChart() {
  seaHighChart.data.datasets[0].data = regionConfigs.map(r => seaHighCurrent[r.name][0]);
  seaHighChart.data.datasets[1].data = regionConfigs.map(r => seaHighCurrent[r.name][1]);
  seaHighChart.data.datasets[2].data = regionConfigs.map(r => seaHighCurrent[r.name][2]);
  seaHighChart.update();
}
