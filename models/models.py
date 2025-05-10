
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, String, Column, Table, Integer, TIMESTAMP
from database.database import Base

# Промежуточная таблица для связи "многие ко многим" между User и Product
user_products = Table(
    'user_products', Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('product_id', ForeignKey('product.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, )
    username: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))

    # Связь с профилем
    profile = relationship("Profile", back_populates="user", uselist=False)
    # Связь с продуктами через промежуточную таблицу
    purchased_products = relationship("Product", secondary=user_products, back_populates="users")


class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    first_name: Mapped[str] = mapped_column(String(50),nullable=True)
    last_name: Mapped[str] = mapped_column(String(50),nullable=True)


    # Связь с пользователем
    user = relationship("User", back_populates="profile")


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Связь с продуктами
    products = relationship("Product", back_populates="category")



class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    Description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)

    # Связь с категорией
    category = relationship("Category", back_populates="products")
    # Связь с пользователями через промежуточную таблицу
    users = relationship("User", secondary=user_products, back_populates="purchased_products")