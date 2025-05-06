import datetime
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, String, Column, Table, Integer, TIMESTAMP
from database.database import Base


# class User(Base):
#     __tablename__ = 'users'
#     telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
#     username: Mapped[str | None] = mapped_column(String(50))
#     first_name: Mapped[str | None] = mapped_column(String(50))
#     last_name: Mapped[str | None] = mapped_column(String(50))
#     profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)
#     def __repr__(self):
#         return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
#
#
#
#
#
# class Category(Base):
#     """
#     Категория товаров. Содержит связь с товарами.
#     """
#     __tablename__ = 'categories'
#
#     category_name: Mapped[str] = mapped_column(Text, nullable=False)
#     products: Mapped[List["Product"]] = relationship(
#         "Product",
#         back_populates="category",
#         cascade="all, delete-orphan"
#     )
#
#     def __repr__(self):
#         return f"<Category(id={self.id}, name='{self.category_name}')>"
#
#
# class Product(Base):
#     """
#     Описывает товар с полями: название, описание, цена,  скрытый контент.
#     """
#     __tablename__ = 'products'
#     name: Mapped[str] = mapped_column(Text)
#     description: Mapped[str] = mapped_column(Text)
#     price: Mapped[int]
#     category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
#     hidden_content: Mapped[str] = mapped_column(Text)
#
#     category: Mapped["Category"] = relationship("Category", back_populates="products")
#     # Отношение для получения покупателей
#     buyers: Mapped[List["Profile"]] = relationship("Profile", back_populates='purchased_products')
#     def __repr__(self):
#         return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
#
#
#
#
#
# class Profile(Base):
#     __tablename__ = 'profiles'
#     user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
#     username: Mapped[str | None] = mapped_column(String(50))
#     first_name: Mapped[str | None] = mapped_column(String(50))
#     last_name: Mapped[str|None] = mapped_column(String(50))
#     # Отношение к пользователю
#     user: Mapped["User"] = relationship("User", back_populates="profile")
#
#     purchased_products: Mapped[List["Product"]] = relationship(
#         "Product",  back_populates="buyers"
#     )
#     def __repr__(self):
#         return (f"<Profile(id={self.id}, user_id={self.user_id}, "
#                 f"username = {self.username},purchased_products = {self.purchased_products},date={self.created_at})>")
class User(Base):
    __tablename__ = 'users'
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = 'profiles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    username: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    user: Mapped["User"] = relationship("User", back_populates="profile")

class Category(Base):
    __tablename__ = 'categories'
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan"
    )

class Product(Base):
    __tablename__ = 'products'  # Явно указываем имя таблицы, если нужно
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    hidden_content: Mapped[str] = mapped_column(Text)
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    buyers: Mapped[List["Profile"]] = relationship(
        "Profile", secondary="purchases", back_populates="purchased_products"
    )

# Таблица ассоциаций для связи пользователей и товаров
purchases_table = Table(
    'purchases', Base.metadata,
    Column('user_id', Integer, ForeignKey('profiles.user_id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('purchase_date', TIMESTAMP)
)

Profile.purchased_products = relationship(
    "Product", secondary=purchases_table, back_populates="buyers"
)