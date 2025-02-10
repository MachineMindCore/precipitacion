-- Database Schema for Hydrological Sensor Data

-- Table to store station information
CREATE TABLE estaciones (
    codigoestacion VARCHAR(20) PRIMARY KEY,
    nombreestacion VARCHAR(100),
    departamento VARCHAR(100),
    municipio VARCHAR(100),
    zonahidrografica VARCHAR(100),
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6)
);

-- Table to store sensor descriptions
CREATE TABLE sensores (
    codigosensor VARCHAR(10) PRIMARY KEY,
    descripcionsensor VARCHAR(100),
    unidadmedida VARCHAR(20)
);

-- Table to store observed values
CREATE TABLE observaciones (
    id SERIAL PRIMARY KEY,
    codigoestacion VARCHAR(20) REFERENCES estaciones(codigoestacion),
    codigosensor VARCHAR(10) REFERENCES sensores(codigosensor),
    fechaobservacion TIMESTAMP,
    valorobservado DECIMAL(10,2)
);

-- Indexes for faster querying
CREATE INDEX idx_fechaobservacion ON observaciones(fechaobservacion);
CREATE INDEX idx_codigoestacion ON observaciones(codigoestacion);
CREATE INDEX idx_codigosensor ON observaciones(codigosensor);
