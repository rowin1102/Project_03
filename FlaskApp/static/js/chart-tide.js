let pieChart2;
function drawChart(labels, values) {
  const data = {
    labels: labels,
    datasets: [{
      data: values,
      backgroundColor: ['#FFB3BA', '#FFDFBA', '#A3D5FF', '#FFFFBA', '#B5EAD7']
    }]
  };

  const config = {
    type: 'pie',
    data: data,
    options: {
      animation: { duration: 1000 },
      plugins: {
        datalabels: {
          color: '#fff',
          font: { weight: 'bold', size: 14 },
          formatter: () => {
            // 파이 내부 라벨 및 퍼센트 표시 안함
            return '';
          }
        },
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: ctx => {
              if (ctx.parsed <= 0.0001) return `${ctx.label}: 데이터 없음`;
              return `${ctx.label}: ${ctx.parsed} m`;
            }
          }
        }
      }
    },
    plugins: [ChartDataLabels]
  };

  if (pieChart2) {
    pieChart2.data = data;
    pieChart2.update();
  } else {
    const ctx = document.getElementById('chart2').getContext('2d');
    pieChart2 = new Chart(ctx, config);
  }
}

async function fetchAndUpdate() {
  try {
    const response = await fetch('/tidedata?t=' + Date.now());  // 캐시 방지
    const json = await response.json();

    const labels = json.map(item => item.name);
    const values = json.map(item => (item.tide_level && item.tide_level > 0) ? item.tide_level : 0.0001);

    drawChart(labels, values);
  } catch (e) {
    console.error('데이터 불러오기 실패:', e);
  }
}
if (document.getElementById('chart2')) {
  fetchAndUpdate();
  setInterval(fetchAndUpdate, 10000);
}