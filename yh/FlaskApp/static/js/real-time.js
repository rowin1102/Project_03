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

// 1) 기존 라인 차트 생성 (wind_speed, sea_high, sea_speed)
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
        pointBackgroundColor: region.color,
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

// 2) 모든 지역 데이터 한번에 로딩 및 라인 차트 초기 10개 데이터 세팅
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

// 3) 기존 라인 차트 5초마다 데이터 1개씩 push
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
        indices[metric][region.name] = 0;
      }
    });

    charts[metric].update();
  });
}, 5000);


// 4) === 여기부터 'chart1'에 실시간 파이차트 생성 및 5개 지역 데이터 표시 ===

// 파이차트 초기 데이터 배열 (0으로 초기화)
let pieDataValues = [0, 0, 0, 0, 0];

// 파이차트용 차트 인스턴스 저장
let pieChart = null;

// chart1 캔버스 컨텍스트 가져오기
const ctxPie = document.getElementById('chart1').getContext('2d');

// 파이차트 초기 생성
function createPieChart() {
  pieChart = new Chart(ctxPie, {
    type: 'pie',
    data: {
      labels: regionConfigs.map(r => r.name),
      datasets: [{
        data: pieDataValues,
        backgroundColor: regionConfigs.map(r => r.color),
        borderColor: '#fff',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right' }
      }
    }
  });
}

// 실시간 파이차트 데이터 업데이트 함수 (예: 5초마다 랜덤 데이터 넣기 - 실제로는 API나 CSV 데이터를 연동하세요)
function updatePieChartData() {
  // 여기선 샘플로 각 지역에 대해 wind_speed 최근값을 pie 데이터로 세팅해봅니다.
  regionConfigs.forEach((region, idx) => {
    const metric = 'wind_speed';
    const buffer = dataBuffers[metric]?.[region.name];
    const index = indices[metric]?.[region.name];

    if (buffer && index !== undefined && buffer.length > 0) {
      // bounds check
      const dataIndex = index > 0 ? index - 1 : 0;
      const value = buffer[dataIndex]?.[metric] ?? 0;
      pieDataValues[idx] = value >= 0 ? value : 0;
    } else {
      pieDataValues[idx] = 0;
    }
  });

  if (pieChart) {
    pieChart.data.datasets[0].data = pieDataValues;
    pieChart.update();
  }
}

// 최초 생성
createPieChart();

// 5초마다 실시간 업데이트 (라인차트랑 동일 주기)
setInterval(() => {
  updatePieChartData();
}, 5000);
