CREATE DATABASE IF NOT EXISTS stugandata;

USE stugandata;

CREATE TABLE IF NOT EXISTS temphumi(
    dtg DATETIME,
    temperature FLOAT(4, 1),
    relative_humidity FLOAT(4, 1),
    sensor_id VARCHAR(10)
);