\set ON_ERROR_STOP on

-- Conectar a la base de datos postgres
\c postgres

-- Eliminar y crear la base de datos geoglows
DROP DATABASE IF EXISTS geoglows;
CREATE DATABASE geoglows;

-- Conectar a la base de datos geoglows
\c geoglows

---------------------------------------------------------------------
--                     drainage network table                      --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drainage_network (
    comid INT NOT NULL PRIMARY KEY,
    latitude NUMERIC,
    longitude NUMERIC,
    river TEXT,
    location1 TEXT,
    location2 TEXT
);

CREATE TABLE IF NOT EXISTS alert_geoglows (
    comid INT NOT NULL REFERENCES drainage_network(comid),
    datetime TIMESTAMP NOT NULL,
    d01 TEXT, d02 TEXT, d03 TEXT, d04 TEXT,
    d05 TEXT, d06 TEXT, d07 TEXT, d08 TEXT,
    d09 TEXT, d10 TEXT, d11 TEXT, d12 TEXT,
    d13 TEXT, d14 TEXT, d15 TEXT, alert TEXT
);

CREATE INDEX idx_alert_geoglows_datetime
    ON alert_geoglows (datetime);

---------------------------------------------------------------------
--                      streamflow data table                      --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS streamflow_stations (
    basin TEXT,
    code TEXT NOT NULL PRIMARY KEY,
    name TEXT,
    latitude NUMERIC,    
    longitude NUMERIC,
    elevation NUMERIC,
    comid INT NOT NULL REFERENCES drainage_network(comid),
    river TEXT,
    location1 TEXT,
    location2 TEXT
);

CREATE TABLE IF NOT EXISTS streamflow_data (
    datetime TIMESTAMP NOT NULL,
    code TEXT NOT NULL REFERENCES streamflow_stations(code),
    value NUMERIC
) PARTITION BY RANGE (datetime);

CREATE TABLE IF NOT EXISTS streamflow_data_1980_1990 
    PARTITION OF streamflow_data
    FOR VALUES FROM ('1980-01-01') TO ('1990-01-01');

CREATE TABLE IF NOT EXISTS streamflow_data_1990_2000 
    PARTITION OF streamflow_data
    FOR VALUES FROM ('1990-01-01') TO ('2000-01-01');

CREATE TABLE IF NOT EXISTS streamflow_data_2000_2010 
    PARTITION OF streamflow_data
    FOR VALUES FROM ('2000-01-01') TO ('2010-01-01');

CREATE TABLE IF NOT EXISTS streamflow_data_2010_2020 
    PARTITION OF streamflow_data
    FOR VALUES FROM ('2010-01-01') TO ('2020-01-01');

CREATE TABLE IF NOT EXISTS streamflow_data_2020_2030 
    PARTITION OF streamflow_data
    FOR VALUES FROM ('2020-01-01') TO ('2030-01-01');

CREATE INDEX idx_streamflow_data_code_datetime 
    ON streamflow_data (code, datetime);

CREATE TABLE IF NOT EXISTS alert_geoglows_streamflow (
    code TEXT NOT NULL REFERENCES streamflow_stations(code),
    datetime TIMESTAMP NOT NULL,
    d01 TEXT, d02 TEXT, d03 TEXT, d04 TEXT,
    d05 TEXT, d06 TEXT, d07 TEXT, d08 TEXT,
    d09 TEXT, d10 TEXT, d11 TEXT, d12 TEXT,
    d13 TEXT, d14 TEXT, d15 TEXT, alert TEXT
);

CREATE INDEX idx_alert_geoglows_steamflow_datetime
    ON alert_geoglows_streamflow (datetime);


---------------------------------------------------------------------
--                      waterlevel data table                      --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS waterlevel_stations (
    basin TEXT,
    code TEXT NOT NULL PRIMARY KEY,
    name TEXT,
    latitude NUMERIC,    
    longitude NUMERIC,
    elevation NUMERIC,
    comid INT NOT NULL REFERENCES drainage_network(comid),
    river TEXT,
    location1 TEXT,
    location2 TEXT
);

CREATE TABLE IF NOT EXISTS waterlevel_data (
    datetime TIMESTAMP NOT NULL,
    code TEXT NOT NULL REFERENCES waterlevel_stations(code),
    value NUMERIC
) PARTITION BY RANGE (datetime);

CREATE TABLE IF NOT EXISTS waterlevel_data_1980_1990 
    PARTITION OF waterlevel_data
    FOR VALUES FROM ('1980-01-01') TO ('1990-01-01');

CREATE TABLE IF NOT EXISTS waterlevel_data_1990_2000 
    PARTITION OF waterlevel_data
    FOR VALUES FROM ('1990-01-01') TO ('2000-01-01');

CREATE TABLE IF NOT EXISTS waterlevel_data_2000_2010 
    PARTITION OF waterlevel_data
    FOR VALUES FROM ('2000-01-01') TO ('2010-01-01');

CREATE TABLE IF NOT EXISTS waterlevel_data_2010_2020 
    PARTITION OF waterlevel_data
    FOR VALUES FROM ('2010-01-01') TO ('2020-01-01');

CREATE TABLE IF NOT EXISTS waterlevel_data_2020_2030 
    PARTITION OF waterlevel_data
    FOR VALUES FROM ('2020-01-01') TO ('2030-01-01');

CREATE INDEX idx_waterlevel_data_code_datetime 
    ON waterlevel_data (code, datetime);

CREATE TABLE IF NOT EXISTS alert_geoglows_waterlevel (
    code TEXT NOT NULL REFERENCES streamflow_stations(code),
    datetime TIMESTAMP NOT NULL,
    d01 TEXT, d02 TEXT, d03 TEXT, d04 TEXT,
    d05 TEXT, d06 TEXT, d07 TEXT, d08 TEXT,
    d09 TEXT, d10 TEXT, d11 TEXT, d12 TEXT,
    d13 TEXT, d14 TEXT, d15 TEXT, alert TEXT
);

CREATE INDEX idx_alert_geoglows_waterlevel_datetime
    ON alert_geoglows_waterlevel (datetime);


---------------------------------------------------------------------
--                   historical simulation data                    --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historical_simulation (
    datetime TIMESTAMP NOT NULL,
    comid INT NOT NULL REFERENCES drainage_network(comid),
    value NUMERIC NOT NULL
) PARTITION BY RANGE (datetime);

CREATE TABLE IF NOT EXISTS historical_simulation_1980_1990 
    PARTITION OF historical_simulation
    FOR VALUES FROM ('1980-01-01') TO ('1990-01-01');

CREATE TABLE IF NOT EXISTS historical_simulation_1990_2000 
    PARTITION OF historical_simulation
    FOR VALUES FROM ('1990-01-01') TO ('2000-01-01');

CREATE TABLE IF NOT EXISTS historical_simulation_2000_2010 
    PARTITION OF historical_simulation
    FOR VALUES FROM ('2000-01-01') TO ('2010-01-01');

CREATE TABLE IF NOT EXISTS historical_simulation_2010_2020 
    PARTITION OF historical_simulation
    FOR VALUES FROM ('2010-01-01') TO ('2020-01-01');

CREATE TABLE IF NOT EXISTS historical_simulation_2020_2030 
    PARTITION OF historical_simulation
    FOR VALUES FROM ('2020-01-01') TO ('2030-01-01');

CREATE INDEX idx_historical_simulation_comid_datetime 
    ON historical_simulation (comid, datetime);

---------------------------------------------------------------------
--                     ensemble forecast data                      --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ensemble_forecast (
    datetime TIMESTAMP NOT NULL,
    ensemble_01 NUMERIC,
    ensemble_02 NUMERIC,
    ensemble_03 NUMERIC,
    ensemble_04 NUMERIC,
    ensemble_05 NUMERIC,
    ensemble_06 NUMERIC,
    ensemble_07 NUMERIC,
    ensemble_08 NUMERIC,
    ensemble_09 NUMERIC,
    ensemble_10 NUMERIC,
    ensemble_11 NUMERIC,
    ensemble_12 NUMERIC,
    ensemble_13 NUMERIC,
    ensemble_14 NUMERIC,
    ensemble_15 NUMERIC,
    ensemble_16 NUMERIC,
    ensemble_17 NUMERIC,
    ensemble_18 NUMERIC,
    ensemble_19 NUMERIC,
    ensemble_20 NUMERIC,
    ensemble_21 NUMERIC,
    ensemble_22 NUMERIC,
    ensemble_23 NUMERIC,
    ensemble_24 NUMERIC,
    ensemble_25 NUMERIC,
    ensemble_26 NUMERIC,
    ensemble_27 NUMERIC,
    ensemble_28 NUMERIC,
    ensemble_29 NUMERIC,
    ensemble_30 NUMERIC,
    ensemble_31 NUMERIC,
    ensemble_32 NUMERIC,
    ensemble_33 NUMERIC,
    ensemble_34 NUMERIC,
    ensemble_35 NUMERIC,
    ensemble_36 NUMERIC,
    ensemble_37 NUMERIC,
    ensemble_38 NUMERIC,
    ensemble_39 NUMERIC,
    ensemble_40 NUMERIC,
    ensemble_41 NUMERIC,
    ensemble_42 NUMERIC,
    ensemble_43 NUMERIC,
    ensemble_44 NUMERIC,
    ensemble_45 NUMERIC,
    ensemble_46 NUMERIC,
    ensemble_47 NUMERIC,
    ensemble_48 NUMERIC,
    ensemble_49 NUMERIC,
    ensemble_50 NUMERIC,
    ensemble_51 NUMERIC,
    ensemble_52 NUMERIC,
    comid INT NOT NULL REFERENCES drainage_network(comid),
    initialized TIMESTAMP NOT NULL
) PARTITION BY RANGE (initialized);

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_06
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_07
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_08
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_09
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_10
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_11
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024_12
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2025_01
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2025_02
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2025_03
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2025_04
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE IF NOT EXISTS ensemble_forecast_2025_05
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');

-- add more tables if necessary

CREATE INDEX idx_ensemble_forecast_comid_initialized
    ON ensemble_forecast (comid, initialized);

---------------------------------------------------------------------
--                      forecast records data                      --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS forecast_records (
    datetime TIMESTAMP NOT NULL,
    comid INT NOT NULL REFERENCES drainage_network(comid),
    value NUMERIC NOT NULL
) PARTITION BY RANGE (datetime);

CREATE TABLE IF NOT EXISTS forecast_records_2024_2025
    PARTITION OF forecast_records
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS forecast_records_2025_2026
    PARTITION OF forecast_records
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE INDEX idx_forecast_records_comid_datetime 
    ON forecast_records (comid, datetime);




CREATE TABLE heatpoint(
    latitude NUMERIC,
    longitude NUMERIC,
    brightness NUMERIC,
    scan NUMERIC,
    track NUMERIC,
    acq_datetime TIMESTAMP NOT NULL,
    confidence TEXT,
    brightness_2 NUMERIC,
    frp NUMERIC
);

CREATE TABLE goes_hotspots(
    latitude NUMERIC,
    longitude NUMERIC,
    datetime TIMESTAMP NOT NULL
);

CREATE INDEX idx_goes_hotspots_datetime
    ON goes_hotspots (datetime);

