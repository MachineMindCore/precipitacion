from sqlalchemy import create_engine, Column, String, Float, Date, ForeignKey, Index
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

class Observacion(Base):
    __tablename__ = 'observaciones'
    id = Column(String(100), primary_key=True)  # Change ID format to 'codigoestacion_date'
    codigoestacion = Column(String(20), ForeignKey('estaciones.codigoestacion'))
    fechaobservacion = Column(Date)  # Store as Date instead of DateTime
    valorobservado = Column(Float(precision=2))

    # Relationships
    estacion = relationship('Estacion', backref='observaciones')
    
# Indexes
Index('idx_fechaobservacion', Observacion.fechaobservacion)
Index('idx_codigoestacion', Observacion.codigoestacion)