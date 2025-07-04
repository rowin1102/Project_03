document.addEventListener('DOMContentLoaded', () => {
  // chart-nav 전체 영역 (시간이동 버튼 포함) div 가져오기
  const chartNavWrap = document.getElementById('chartNavWrap');

  // 주요 버튼들 id로 가져오기
  const windDirBtn = document.getElementById('windDirBtn');
  const seaDirBtn = document.getElementById('seaDirBtn');
  const tideBtn = document.getElementById('tideBtn');
  const pressureBtn = document.getElementById('pressureBtn');
  const windSpeedBtn = document.getElementById('windSpeedBtn');
  const seaSpeedBtn = document.getElementById('seaSpeedBtn');

  // 풍향, 유향 버튼 클릭하면 시간 이동 버튼 숨김
  if (windDirBtn) {
    windDirBtn.addEventListener('click', () => {
      if (chartNavWrap) chartNavWrap.style.display = 'none';
    });
  }
  if (seaDirBtn) {
    seaDirBtn.addEventListener('click', () => {
      if (chartNavWrap) chartNavWrap.style.display = 'none';
    });
  }

  // 해수면, 기압, 풍속, 유속 버튼 클릭하면 시간 이동 버튼 다시 보임
  [tideBtn, pressureBtn, windSpeedBtn, seaSpeedBtn].forEach(btn => {
    if (btn) {
      btn.addEventListener('click', () => {
        if (chartNavWrap) chartNavWrap.style.display = 'flex'; // flex 아니면 block 상황 맞게
      });
    }
  });
});
