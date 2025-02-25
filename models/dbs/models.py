import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from models.databases import Base

    
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    full_name: Mapped[str]
    username: Mapped[str] = mapped_column(nullable=True)
    admin: Mapped[bool] = mapped_column(default=False)
    
class Estate(Base):
    __tablename__ = 'estates'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    description: Mapped[str]
    photos: Mapped[list['Photo']] = relationship('Photo', back_populates='estate')
    phone: Mapped[str]
    trade_to: Mapped[str]
    created_at: Mapped[str] = mapped_column(default=datetime.datetime.now)

class Photo(Base):
    __tablename__ = 'photos'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    estate_id: Mapped[int] = mapped_column(ForeignKey('estates.id'))
    file_id: Mapped[str]  
      
    estate: Mapped[Estate] = relationship('Estate', back_populates='photos')
