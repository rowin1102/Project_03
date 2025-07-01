const metrics = ['wind_speed', 'sea_high', 'sea_speed'];
const regionConfigs = [
  { name: '태안', files: ['Taean_05.csv', 'Taean_04.csv'], color: 'red' },
  { name: '인천', files: ['InCheon_04.csv', 'InCheon_04.csv'], color: 'blue' },
  { name: '통영', files: ['TongYeong_04.csv', 'TongYeong_05.csv'], color: 'green' },
  { name: '여수', files: ['Yeosu_04.csv', 'Yeosu_05.csv'], color: 'orange' },
  { name: '울진', files: ['Uljin_04.csv', 'Uljin_05.csv'], color: 'purple' },
];

// 각 그래프용 Chart 인스턴스 저장
const charts = {};

// 각 컬럼별로 데이터 버퍼와 인덱스 따로
const dataBuffers = {};
const indices = {};

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
        borderColor: region.color,
        borderWidth: 2,
        fill: false,
        tension: 0.6,
        pointRadius: 2,
        pointBackgroundColor:region.color,
        pointBorderColor: region.color,
        pointBorderWidth: 2,
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
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            usePointStyle: true,   // ✔ 점 스타일 쓰겠다
            pointStyle: 'line',    // ✔ 범례 아이콘을 선 모양으로
            boxWidth: 100,          // ✔ 선 길이 조절
            boxHeight: 7,          // ✔ 선 두께 조절
          }
    },
    tooltip: { enabled: true }
  },
    }
  });
});

// ✅ 모든 지역 데이터 한번에 로딩
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

      dataBuffers[metric][region.name] = allData;
      indices[metric][region.name] = 0;

      // ✅ 각 그래프 초기 10개 push
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

      charts[metric].update();
    });
  });
});

// ✅ 이후 5초마다 각 컬럼/지역 데이터 1개씩 push
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
          x: dataset.data.length,
          y: value
        });

        if (dataset.data.length > 50) {
          dataset.data.shift();
        }
      }

      indices[metric][region.name]++;
      if (indices[metric][region.name] >= buffer.length) {
        indices[metric][region.name] = 0; // 반복
      }
    });

    charts[metric].update();
  });
}, 5000);
