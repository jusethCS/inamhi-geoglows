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
CREATE TABLE IF NOT EXISTS streamflow_station (
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
CREATE TABLE IF NOT EXISTS waterlevel_station (
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
    datetime DATETIME NOT NULL,
    comid INT NOT NULL,
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
    ensemble_52 NUMERIC
) PARTITION BY RANGE (initialized);

CREATE TABLE IF NOT EXISTS ensemble_forecast_2024
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
    
CREATE TABLE IF NOT EXISTS ensemble_forecast_2025 
    PARTITION OF ensemble_forecast
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');