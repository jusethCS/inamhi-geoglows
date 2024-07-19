\set ON_ERROR_STOP on
\c postgres

\echo
\echo
\echo

\c postgres

DROP DATABASE geoglows;
CREATE DATABASE geoglows;

\c geoglows

CREATE TABLE IF NOT EXISTS drainage_network (
    comid INT NOT NULL PRIMARY KEY,
    latitude NUMERIC,
    longitude NUMERIC,
    river TEXT,
    location1 TEXT,
    location2 TEXT,
    alert TEXT NOT NULL
);



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
    comid INT NOT NULL,
    river TEXT,
    location1 TEXT,
    location2 TEXT,
    alert TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS streamflow_data (
    datetime DATE NOT NULL,
    code TEXT NOT NULL,
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




---------------------------------------------------------------------
--                      streamflow data table                      --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS waterlevel_stations (
    basin TEXT,
    code TEXT NOT NULL PRIMARY KEY,
    name TEXT,
    latitude NUMERIC,	
    longitude NUMERIC,
    elevation NUMERIC,
    comid INT NOT NULL,
    river TEXT,
    location1 TEXT,
    location2 TEXT,
    alert TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS waterlevel_data (
    datetime DATE NOT NULL,
    code TEXT NOT NULL,
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




---------------------------------------------------------------------
--                   historical simulation data                    --
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historical_simulation (
    datetime DATE NOT NULL,
    comid INT NOT NULL,
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



CREATE TABLE IF NOT EXISTS ensemble_forecast (
    initialized DATE NOT NULL,
    datetime TIMESTAMP NOT NULL,
    comid INT NOT NULL,
    ensemble_01_m^3/s NUMERIC,
    ensemble_02_m^3/s NUMERIC,
    ensemble_03_m^3/s NUMERIC,
    ensemble_04_m^3/s NUMERIC,
    ensemble_05_m^3/s NUMERIC,
    ensemble_06_m^3/s NUMERIC,
    ensemble_07_m^3/s NUMERIC,
    ensemble_08_m^3/s NUMERIC,
    ensemble_09_m^3/s NUMERIC,
    ensemble_10_m^3/s NUMERIC,
    ensemble_11_m^3/s NUMERIC,
    ensemble_12_m^3/s NUMERIC,
    ensemble_13_m^3/s NUMERIC,
    ensemble_14_m^3/s NUMERIC,
    ensemble_15_m^3/s NUMERIC,
    ensemble_16_m^3/s NUMERIC,
    ensemble_17_m^3/s NUMERIC,
    ensemble_18_m^3/s NUMERIC,
    ensemble_19_m^3/s NUMERIC,
    ensemble_20_m^3/s NUMERIC,
    ensemble_21_m^3/s NUMERIC,
    ensemble_22_m^3/s NUMERIC,
    ensemble_23_m^3/s NUMERIC,
    ensemble_24_m^3/s NUMERIC,
    ensemble_25_m^3/s NUMERIC,
    ensemble_26_m^3/s NUMERIC,
    ensemble_27_m^3/s NUMERIC,
    ensemble_28_m^3/s NUMERIC,
    ensemble_29_m^3/s NUMERIC,
    ensemble_30_m^3/s NUMERIC,
    ensemble_31_m^3/s NUMERIC,
    ensemble_32_m^3/s NUMERIC,
    ensemble_33_m^3/s NUMERIC,
    ensemble_34_m^3/s NUMERIC,
    ensemble_35_m^3/s NUMERIC,
    ensemble_36_m^3/s NUMERIC,
    ensemble_37_m^3/s NUMERIC,
    ensemble_38_m^3/s NUMERIC,
    ensemble_39_m^3/s NUMERIC,
    ensemble_40_m^3/s NUMERIC,
    ensemble_41_m^3/s NUMERIC,
    ensemble_42_m^3/s NUMERIC,
    ensemble_43_m^3/s NUMERIC,
    ensemble_44_m^3/s NUMERIC,
    ensemble_45_m^3/s NUMERIC,
    ensemble_46_m^3/s NUMERIC,
    ensemble_47_m^3/s NUMERIC,
    ensemble_48_m^3/s NUMERIC,
    ensemble_49_m^3/s NUMERIC,
    ensemble_50_m^3/s NUMERIC,
    ensemble_51_m^3/s NUMERIC,
    ensemble_52_m^3/s NUMERIC
) PARTITION BY RANGE (initialized);

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
    
CREATE TABLE IF NOT EXISTS ensemble_forecast_2025 
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');