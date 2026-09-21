from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Pokemon(Base):
    __tablename__ = "Pokemon"

    id          = Column("Id", Integer, primary_key=True, autoincrement = True)
    dex_number  = Column("DexNumber", Integer, nullable=False)
    name        = Column("Name", String, nullable=False)
    type_one    = Column("Type1", String, nullable=False)
    type_two    = Column("Type2", String)
    generation  = Column("Generation", Integer, nullable=False)
    form = Column("Form", String)
    total = Column("Total", Integer)
    hp = Column("HP", Integer)
    attack = Column("Attack", Integer)
    defense = Column("Defense", Integer)
    special_attack = Column("SpecialAttack", Integer)
    special_defense = Column("SpecialDefense", Integer)
    speed = Column("Speed", Integer)
