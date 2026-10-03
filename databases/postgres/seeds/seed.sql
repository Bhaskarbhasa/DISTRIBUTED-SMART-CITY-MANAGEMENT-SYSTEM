-- Seed file for initial testing data

-- Devices
INSERT INTO devices (zone_id, type, status, firmware_version, coordinates) VALUES
(1, 'TRAFFIC_CAMERA', 'ONLINE', 'v2.1.0', '{"lat": 40.7128, "lon": -74.0060}'),
(1, 'TRAFFIC_LIGHT', 'ONLINE', 'v1.5.2', '{"lat": 40.7129, "lon": -74.0061}'),
(2, 'AIR_QUALITY_SENSOR', 'ONLINE', 'v3.0.1', '{"lat": 40.7150, "lon": -74.0100}'),
(2, 'SMART_STREETLIGHT', 'OFFLINE', 'v1.1.0', '{"lat": 40.7155, "lon": -74.0110}'),
(3, 'TRAFFIC_CAMERA', 'ONLINE', 'v2.1.0', '{"lat": 40.7080, "lon": -74.0020}'),
(3, 'WATER_LEVEL_SENSOR', 'ONLINE', 'v1.0.0', '{"lat": 40.7085, "lon": -74.0025}'),
(4, 'SMART_STREETLIGHT', 'ONLINE', 'v1.2.0', '{"lat": 40.7200, "lon": -74.0150}'),
(4, 'TRAFFIC_LIGHT', 'ONLINE', 'v1.5.2', '{"lat": 40.7205, "lon": -74.0155}'),
(5, 'AIR_QUALITY_SENSOR', 'MAINTENANCE', 'v3.0.1', '{"lat": 40.7180, "lon": -73.9900}'),
(5, 'TRAFFIC_CAMERA', 'ONLINE', 'v2.1.0', '{"lat": 40.7185, "lon": -73.9905}');

-- Traffic Configurations
INSERT INTO traffic_configurations (zone_id, config_data, updated_by) VALUES
(1, '{"cycle_time": 90, "green_ratio": 0.6, "mode": "ADAPTIVE"}', 2),
(2, '{"cycle_time": 60, "green_ratio": 0.5, "mode": "FIXED"}', 2),
(3, '{"cycle_time": 120, "green_ratio": 0.7, "mode": "ADAPTIVE"}', 2);

-- System Config
INSERT INTO system_config (key, value) VALUES
('ALERT_THRESHOLDS', '{"air_quality_aqi": 100, "traffic_congestion_level": 8}'),
('GLOBAL_MAINTENANCE_MODE', 'false');
