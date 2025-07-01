def detect_abnormal(data):
    result = []
    if 'tide_level' in data and data['tide_level'] < 80:
        result.append('조위 (위험)')
    elif 'tide_level' in data and data['tide_level'] < 100:
        result.append('조위 (주의)')
        
    if 'wind_speed' in data and data['wind_speed'] > 8:
        result.append('풍속 (위험)')
    elif 'wind_speed' in data and data['wind_speed'] > 6:
        result.append('풍속 (주의)')

    if 'current_speed' in data and data['current_speed'] > 70:
        result.append('유속 (위험)')
    elif 'current_speed' in data and data['current_speed'] > 60:
        result.append('유속 (주의)')

    if 'air_temp' in data and (data['air_temp'] < -2 or data['air_temp'] > 35):
        result.append('기온 (위험)')
    elif 'air_temp' in data and (data['air_temp'] < 0 or data['air_temp'] > 30):
        result.append('기온 (주의)')

    if 'air_press' in data and (data['air_press'] < 990 or data['air_press'] > 1030):
        result.append('기압 (위험)')
    elif 'air_press' in data and (data['air_press'] < 995 or data['air_press'] > 1025):
        result.append('기압 (주의)')

    if 'water_temp' in data and (data['water_temp'] < -1 or data['water_temp'] > 33):
        result.append('수온 (위험)')
    elif 'water_temp' in data and (data['water_temp'] < 0 or data['water_temp'] > 30):
        result.append('수온 (주의)')

    return result