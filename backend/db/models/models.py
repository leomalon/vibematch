from sqlalchemy import Column, Integer, String,ForeignKey,DateTime,Date,Time, Numeric,Text,Boolean,Table
from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy.sql import func

Base = declarative_base() #Any class that inherits from Base is a database table mapping

#Association tables

experiencia_categoria = Table(
    "experiencia_categoria",
    Base.metadata,
    Column("experiencia_id", Integer, ForeignKey("experiencia.id"), primary_key=True),
    Column("categoria_id", Integer, ForeignKey("categoria.id"), primary_key=True),
)

experiencia_compania = Table(
    "experiencia_compania",
    Base.metadata,
    Column("experiencia_id", Integer, ForeignKey("experiencia.id"), primary_key=True),
    Column("compania_id", Integer, ForeignKey("compania.id"), primary_key=True),
)

experiencia_tag = Table(
    "experiencia_tag",
    Base.metadata,
    Column("experiencia_id", Integer, ForeignKey("experiencia.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)



#Catalogs
class Pais(Base):
    __tablename__="pais"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)

    ciudades = relationship(
        "Ciudad",
        back_populates="pais"
    )

class Ciudad(Base):
    __tablename__="ciudad"

    id = Column(Integer,primary_key=True)
    pais_id = Column(Integer, ForeignKey("pais.id"))
    nombre = Column(String,unique=True)

    pais = relationship(
        "Pais",
        back_populates="ciudades"
    )

    distritos = relationship(
        "Distrito",
        back_populates="ciudad"
    )

class Distrito(Base):
    __tablename__ = "distrito"

    id = Column(Integer,primary_key=True)
    ciudad_id = Column(Integer, ForeignKey("ciudad.id"))
    nombre = Column(String, unique=True)

    ciudad = relationship(
        "Ciudad",
        back_populates="distritos"
    )


class Tipo(Base):
    __tablename__ = "tipo_experiencia"

    id = Column(Integer,primary_key=True)
    nombre = Column(String, unique=True)

    experiencias = relationship(
        "Experiencia",
        back_populates="tipo"
    )


class Compania(Base):
    __tablename__ = "compania"

    id = Column(Integer,primary_key=True)
    nombre = Column(String, unique=True)

    experiencias = relationship(
        "Experiencia",
        secondary=experiencia_compania,
        back_populates="companias"
    )


class Mood(Base):
    __tablename__ = "mood"

    id = Column(Integer,primary_key=True)
    nombre = Column(String, unique=True)

    experiencia_moods = relationship(
        "ExperienciaMood",
        back_populates="mood"
    )

class Categoria(Base):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)

    experiencias = relationship(
        "Experiencia",
        secondary=experiencia_categoria,
        back_populates="categorias"
    )


#Primary tables

class Experiencia(Base):
    __tablename__ = "experiencia"

    id = Column(Integer,primary_key=True)
    tipo_id = Column(Integer, ForeignKey("tipo_experiencia.id"),nullable=False)
    titulo = Column(String,nullable=False)
    descripcion = Column(Text)
    es_permanente = Column(Boolean,nullable=False)
    precio_min = Column(Numeric)
    precio_max = Column(Numeric)
    duracion_minutos = Column(Integer)
    link_externo = Column(Text)
    imagen_principal = Column(Text)
    negocio_id = Column(Integer,ForeignKey("negocio.id"))
    creado_a =  Column(
        DateTime,
        server_default=func.now()
    )
    actualizado_a = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    tipo = relationship(
        "Tipo",
        back_populates="experiencias"
    )

    categorias = relationship(
        "Categoria",
        secondary=experiencia_categoria,
        back_populates="experiencias"
    )

    programaciones = relationship(
        "Programacion",
        back_populates="experiencias"
    )

    companias = relationship(
        "Compania",
        secondary=experiencia_compania,
        back_populates="experiencias"
    )

    tags = relationship(
        "Tag",
        secondary=experiencia_tag,
        back_populates="experiencias"
    )

    experiencia_moods = relationship(
        "ExperienciaMood",
        back_populates="experiencia",
        cascade="all, delete-orphan"
    )

    ubicaciones = relationship(
        "Ubicacion",
        back_populates="experiencias"
    )

    negocio = relationship(
        "Negocio",
        back_populates="experiencias"
    )


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer,primary_key=True)
    nombre = Column(String,nullable=False,unique=True)

    experiencias = relationship(
        "Experiencia",
        secondary=experiencia_tag,
        back_populates="tags"
    )

class Fuente(Base):
    __tablename__ = "fuente"

    id = Column(Integer,primary_key=True)
    nombre = Column(String,nullable=False)

    negocios = relationship(
        "Negocio",
        back_populates="fuente"
    )

class Negocio(Base):
    __tablename__ = "negocio"

    id = Column(Integer,primary_key=True)
    fuente_id = Column(Integer,ForeignKey("fuente.id"),nullable=False)
    nombre = Column(String,nullable=False)

    fuente = relationship(
        "Fuente",
        back_populates="negocios"
    )

    experiencias = relationship(
        "Experiencia",
        back_populates="negocio"
    )


class Programacion(Base):
    __tablename__ = "programacion"

    id = Column(Integer,primary_key=True)
    experiencia_id = Column(Integer,ForeignKey("experiencia.id"),nullable=False)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)

    experiencias = relationship(
        "Experiencia",
        back_populates="programaciones"
    )

class Ubicacion(Base):
    __tablename__ = "ubicacion"

    id = Column(Integer,primary_key=True)
    pais_id = Column(Integer,ForeignKey("pais.id"),nullable=False)
    ciudad_id = Column(Integer,ForeignKey("ciudad.id"),nullable=False)
    distrito_id = Column(Integer,ForeignKey("distrito.id"),nullable=False)
    direccion = Column(Text)
    latitud = Column(Numeric)
    longitud = Column(Numeric)
    experiencia_id = Column(Integer,ForeignKey("experiencia.id"),nullable=False)


    experiencias = relationship(
        "Experiencia",
        back_populates="ubicaciones"
    )




#Relationship tables
class ExperienciaMood(Base):
    __tablename__ = "experiencia_mood"

    experiencia_id = Column(
        Integer,
        ForeignKey("experiencia.id"),
        primary_key=True
    )

    mood_id = Column(
        Integer,
        ForeignKey("mood.id"),
        primary_key=True
    )

    peso = Column(Numeric, nullable=False,default=1.0)

    experiencia = relationship(
        "Experiencia",
        back_populates="experiencia_moods"
    )

    mood = relationship(
        "Mood",
        back_populates="experiencia_moods"
    )

