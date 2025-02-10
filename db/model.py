from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# SQLAlchemy Base
Base = declarative_base()

# SQLAlchemy Models
class Estacion(Base):
    __tablename__ = 'estaciones'
    codigoestacion = Column(String(20), primary_key=True)
    nombreestacion = Column(String(100))
    departamento = Column(String(100))
    municipio = Column(String(100))
    zonahidrografica = Column(String(100))
    latitud = Column(Float(precision=6))
    longitud = Column(Float(precision=6))

class Sensor(Base):
    __tablename__ = 'sensores'
    codigosensor = Column(String(10), primary_key=True)
    descripcionsensor = Column(String(100))
    unidadmedida = Column(String(20))

class Observacion(Base):
    __tablename__ = 'observaciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigoestacion = Column(String(20), ForeignKey('estaciones.codigoestacion'))
    codigosensor = Column(String(10), ForeignKey('sensores.codigosensor'))
    fechaobservacion = Column(DateTime)
    valorobservado = Column(Float(precision=2))

    # Relationships
    estacion = relationship('Estacion', backref='observaciones')
    sensor = relationship('Sensor', backref='observaciones')

# Indexes
Index('idx_fechaobservacion', Observacion.fechaobservacion)
Index('idx_codigoestacion', Observacion.codigoestacion)
Index('idx_codigosensor', Observacion.codigosensor)