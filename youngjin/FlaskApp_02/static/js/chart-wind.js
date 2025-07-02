let pieChart1;
function drawPieChart(labels, values) {
    const total = values.reduce((sum, val) => sum + val, 0);
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
            display: false,
            formatter: (value, ctx) => {
              if(value <= 0.0001) return '';
              const percent = total ? (value / total * 100).toFixed(1) + '%' : '0%';
              return `${ctx.chart.data.labels[ctx.dataIndex]}\n${percent}`;
            }
          },
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: ctx => {
                if (ctx.parsed <= 0.0001) return `${ctx.label}: 데이터 없음`;
                return `${ctx.label}: ${ctx.parsed} m/s`;
              }
            }
          }
        }
      },
      plugins: [ChartDataLabels]
    };
    if (pieChart1) {
      pieChart1.data = data;
      pieChart1.update();
    } else {
      const ctx = document.getElementById('chart1').getContext('2d');
      pieChart1 = new Chart(ctx, config);
    }
}

async function fetchAndUpdatePie() {
    try {
      const response = await fetch('/winddata?t=' + Date.now());
      const json = await response.json();
      const labels = json.map(item => item.name);
      const values = json.map(item => (item.wind_speed && item.wind_speed > 0) ? item.wind_speed : 0.0001);
      drawPieChart(labels, values);
    } catch (e) {
      console.error('데이터 불러오기 실패:', e);
    }
}
if (document.getElementById('chart1')) {
    fetchAndUpdatePie();
    setInterval(fetchAndUpdatePie, 10000);
}
