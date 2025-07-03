let currentStartTime = new Date("2025-05-31T22:00:00");
const showDurationHours = 4;

let rawData = {
  observed: [],
  predicted: []
};
let currentType = "sea_high"; // default

const titleMap = {
  sea_high: "해수면의 높이",
  wind_speed: "풍속",
  pressure: "기압",
  sea_speed: "유속",
  wind_dir: "풍향",
  current_dir: "유향"
};

async function fetchChartData() {
  const res = await fetch("/api/incheon_chart_data");
  const data = await res.json();
  rawData = data;
  drawChart(currentType);
}

function updateTimeRangeLabel() {
  const end = new Date(currentStartTime.getTime() + showDurationHours * 60 * 60 * 1000);
  const format = (d) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:00`;

  const label = `${format(currentStartTime)} ~ ${format(end)}`;
  const rangeEl = document.getElementById("chartTimeRange");
  if (rangeEl) {
    rangeEl.innerText = label;
  }
}

function drawChart(type) {
  const canvas = document.getElementById("incheonChart");
  const chartPlaceholder = document.getElementById("chartPlaceholder");

  // --- 차트 show/hide 컨트롤 ---
  if (type === "wind_dir" || type === "current_dir") {
    // 풍향/유향 버튼: canvas 숨기고 polar 차트만 보임
    if (canvas) canvas.style.display = "none";
    if (chartPlaceholder) chartPlaceholder.style.display = "block";
    updateTimeRangeLabel();
    const titleEl = document.getElementById("chartTitle");
    if (titleEl) {
      titleEl.innerText = `${titleMap[type]} 변화 추이`;
    }
    return;
  } else {
    // 나머지 4개: canvas 보이고, polar 차트는 숨김
    if (canvas) canvas.style.display = "block";
    if (chartPlaceholder) chartPlaceholder.style.display = "none";
  }
  // --------------------------

  if (!canvas) {
    console.error("canvas 요소를 찾을 수 없습니다.");
    return;
  }

  const ctx = canvas.getContext("2d");
  if (window.myChart) {
    window.myChart.destroy();
  }

  const start = new Date(currentStartTime);
  const end = new Date(start.getTime() + showDurationHours * 60 * 60 * 1000);
  const cutoff = new Date("2025-06-01T00:00:00");

  const allData = [
    ...rawData.observed,
    ...rawData.predicted
  ]
    .map((d) => ({ x: new Date(d.datetime), y: d[type] }))
    .filter((d) => d.x >= start && d.x <= end);

  // 실측: 5월까지만
  const observed = allData.filter((d) => d.x < cutoff);
  // 예측: 6월부터
  const predicted = allData.filter((d) => d.x >= cutoff);

  window.myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "5월 (실측)",
          data: observed,
          borderColor: "#007bff",
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.5,
        },
        {
          label: "6월 (예측)",
          data: predicted,
          borderColor: "#ff0000",
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.5,
          borderDash: [5, 5], // 점선
        }
      ],
    },
    options: {
      animation: {
        duration: 0
      },
      parsing: false,
      responsive: true,
      scales: {
        x: {
          type: "time",
          time: {
            unit: "hour",
            tooltipFormat: "yyyy-MM-dd HH:mm",
            displayFormats: {
              hour: "yyyy-MM-dd HH:00",
            },
          },
          min: start,
          max: end,
          ticks: {
            source: "auto",
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0,
          },
          title: {
            display: true,
            text: "시간",
          },
        },
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: type,
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });

  updateTimeRangeLabel();

  const titleEl = document.getElementById("chartTitle");
  if (titleEl) {
    titleEl.innerText = `${titleMap[type]} 변화 추이`;
  }
}

window.addEventListener("load", () => {
  fetchChartData();

  document.querySelectorAll(".column-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentType =
        btn.innerText === "해수면의 높이"
          ? "sea_high"
          : btn.innerText === "풍속"
          ? "wind_speed"
          : btn.innerText === "기압"
          ? "pressure"
          : btn.innerText === "유속"
          ? "sea_speed"
          : btn.innerText === "풍향"
          ? "wind_dir"
          : btn.innerText === "유향"
          ? "current_dir"
          : "sea_high";

      document.querySelectorAll(".column-btn").forEach((b) =>
        b.classList.remove("active")
      );
      btn.classList.add("active");

      drawChart(currentType);

      // 풍향/유향 이외의 버튼 클릭 시 Plotly 애니메이션 중단 추가(옵션)
      // window.clearInterval(window.windDirInterval);
      // Plotly.purge("chartPlaceholder"); // 필요하면 정리
    });
  });

  const prev = document.getElementById("prevHour");
  const next = document.getElementById("nextHour");

  if (prev && next) {
    prev.addEventListener("click", () => {
      currentStartTime.setHours(currentStartTime.getHours() - 1);
      drawChart(currentType);
    });

    next.addEventListener("click", () => {
      currentStartTime.setHours(currentStartTime.getHours() + 1);
      drawChart(currentType);
    });
  }
});
