// const regionConfigs = [
//   { name: '태안', files: ['Taean_05.csv', 'Taean_04.csv'], color: 'red' },
//   { name: '인천', files: ['InCheon_04.csv', 'InCheon_04.csv'], color: 'blue' },
//   { name: '통영', files: ['TongYeong_04.csv', 'TongYeong_05.csv'], color: 'green' },
//   { name: '여수', files: ['Yeosu_04.csv', 'Yeosu_05.csv'], color: 'orange' },
//   { name: '울진', files: ['Uljin_04.csv', 'Uljin_05.csv'], color: 'purple' },
// ];

// const ctx = document.getElementById("chart2").getContext('2d');
    // const regionConfigs = [
    //   { name: '태안', files: ['Taean_05.csv', 'Taean_04.csv'], color: 'red' },
    //   { name: '인천', files: ['InCheon_04.csv', 'InCheon_04.csv'], color: 'blue' },
    //   { name: '통영', files: ['TongYeong_04.csv', 'TongYeong_05.csv'], color: 'green' },
    //   { name: '여수', files: ['Yeosu_04.csv', 'Yeosu_05.csv'], color: 'orange' },
    //   { name: '울진', files: ['Uljin_04.csv', 'Uljin_05.csv'], color: 'purple' },
    // ];

    // 파이 차트용 데이터 준비
    const labels = regionConfigs.map(region => region.name);
    const data = regionConfigs.map(region => region.files.length);
    const backgroundColors = regionConfigs.map(region => region.color);

    // 차트 생성
    const ctx = document.getElementById("chart2").getContext('2d');
    const pieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: backgroundColors,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.label}: ${context.parsed}개`;
              }
            }
          }
        }
      }
    });
  