// 외부 CDN 스크립트 로드 (Chart.js + ChartDataLabels 플러그인)
function loadScript(src, callback) {
  const script = document.createElement('script');
  script.src = src;
  script.onload = callback;
  document.head.appendChild(script);
}

// DOM과 차트 구성
function setupPage() {
  // 제목 추가
  const title = document.createElement('h2');
  title.textContent = '실시간 풍속 비율 (인천, 통영, 태안, 여수, 울진)';
  document.body.appendChild(title);

  // 캔버스 추가
  const canvas = document.createElement('canvas');
  canvas.id = 'windChart';
  canvas.style.maxWidth = '600px';
  canvas.style.margin = 'auto';
  document.body.appendChild(canvas);

  // 기본 스타일 적용
  document.body.style.fontFamily = 'Arial, sans-serif';
  document.body.style.textAlign = 'center';
  document.body.style.marginTop = '40px';
}

let chart = null;

function drawChart(labels, values) {
  const total = values.reduce((sum, val) => sum + val, 0);

  const data = {
    labels: labels,
    datasets: [{
      data: values,
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
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
          formatter: (value, ctx) => {
            const percent = total ? (value / total * 100).toFixed(1) + '%' : '0%';
            return `${ctx.chart.data.labels[ctx.dataIndex]}\n${percent}`;
          }
        },
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.label}: ${ctx.parsed} m/s`
          }
        }
      }
    },
    plugins: [ChartDataLabels]
  };

  if (chart) {
    chart.data = data;
    chart.update();
  } else {
    const ctx = document.getElementById('windChart').getContext('2d');
    chart = new Chart(ctx, config);
  }
}

async function fetchAndUpdate() {
  try {
    const response = await fetch('/winddata?t=' + Date.now());  // 캐시 방지
    const json = await response.json();

    const labels = json.map(item => item.name);
    const values = json.map(item => item.wind_speed);

    drawChart(labels, values);
  } catch (e) {
    console.error('데이터 불러오기 실패:', e);
  }
}

// 순차적으로 스크립트 로드 및 실행
loadScript('https://cdn.jsdelivr.net/npm/chart.js', () => {
  loadScript('https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2', () => {
    document.addEventListener('DOMContentLoaded', () => {
      setupPage();
      fetchAndUpdate();
      setInterval(fetchAndUpdate, 10000);  // 10초마다 갱신
    });
  });
});
