// 분석용 파이차트 데이터 및 설정
const analysisLabels = ['조위', '풍속', '유속', '기온', '기압', '수온'];
const analysisMetrics = ['tide_level', 'wind_speed', 'current_speed', 'air_temp', 'air_press', 'water_temp'];
const analysisRegions = ['태안', '인천', '통영', '여수', '울진'];
const analysisFiles = {
  '태안': ['Taean_05.csv', 'Taean_04.csv'],
  '인천': ['InCheon_04.csv', 'InCheon_04.csv'],
  '통영': ['TongYeong_04.csv', 'TongYeong_05.csv'],
  '여수': ['Yeosu_04.csv', 'Yeosu_05.csv'],
  '울진': ['Uljin_04.csv', 'Uljin_05.csv'],
};

const analysisTotals = {
  tide_level: 0,
  wind_speed: 0,
  current_speed: 0,
  air_temp: 0,
  air_press: 0,
  water_temp: 0,
};

// CSV를 읽고 항목별 합산 함수 (비동기)
async function loadAndSumAnalysisData() {
  for (const region of analysisRegions) {
    const csvTexts = await Promise.all(
      analysisFiles[region].map(file =>
        fetch(`/static/finalData/${file}`).then(res => res.text())
      )
    );

    const allData = csvTexts.flatMap(csvText =>
      Papa.parse(csvText, { header: true, dynamicTyping: true }).data
    );

    analysisMetrics.forEach(metric => {
      allData.forEach(row => {
        const val = row[metric];
        if (val !== undefined && val !== null && isFinite(val)) {
          analysisTotals[metric] += val;
        }
      });
    });
  }
}

// 파이차트 생성 함수
async function createAnalysisPieChart() {
  await loadAndSumAnalysisData();

  const ctx = document.getElementById('chart2').getContext('2d');

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: analysisLabels,
      datasets: [{
        label: '항목별 합계 (태안, 인천, 통영, 여수, 울진)',
        data: analysisMetrics.map(m => analysisTotals[m]),
        backgroundColor: ['#4dd0e1', '#81c784', '#ffb74d', '#9575cd', '#f06292', '#90a4ae'],
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.label}: ${ctx.raw.toFixed(2)}`
          }
        }
      }
    }
  });
}

// DOMContentLoaded 이벤트에 연결
document.addEventListener('DOMContentLoaded', () => {
  createAnalysisPieChart();
});
