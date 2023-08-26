from typing import List

import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, ForeignKey, func

DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
app = FastAPI()
connect = None

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
)

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(128)),
    sqlalchemy.Column("price", sqlalchemy.REAL),
    sqlalchemy.Column("stock_balance", sqlalchemy.Integer),
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, ForeignKey('users.id')),
    sqlalchemy.Column("delivered", sqlalchemy.BOOLEAN, default=False),
)

order_items = sqlalchemy.Table(
    "order_items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("order_id", sqlalchemy.Integer, ForeignKey('orders.id')),
    sqlalchemy.Column("product_id", sqlalchemy.Integer, ForeignKey('products.id')),
    sqlalchemy.Column("quantity", sqlalchemy.Integer),
    sqlalchemy.Column("price", sqlalchemy.REAL),
)

products_balance = sqlalchemy.Table(
    "products_balance",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("product_id", sqlalchemy.Integer, ForeignKey('products.id')),
    sqlalchemy.Column("quantity", sqlalchemy.Integer),
)

# Создание БД
'''engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)'''


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class IncountBalanse(BaseModel):
    product_id: int
    quantity: int = Field(ge=0)


class User(BaseModel):
    id: int = Field(default=None)
    name: str = Field(max_length=32)
    email: str = Field(max_length=128)


class Product(BaseModel):
    id: int = Field(default=None)
    name: str = Field(max_length=32)
    price: float


class Order_item(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=0)


class Order(BaseModel):
    id: int = Field(default=0)
    user_id: int = Field(ge=1)
    delivered: bool = Field(default=False)
    price: float
    items: List[Order_item]


@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.post('/users/', response_model=User)
async def add_user(new_user: User):
    query = users.insert().values(name=new_user.name, email=new_user.email)
    last_record_id = await database.execute(query)
    return {**new_user.model_dump(), "id": last_record_id}


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int = Path(..., ge=1)):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(new_user: User, user_id: int = Path(..., ge=1)):
    new_user.id = user_id
    query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
    await database.execute(query)
    return {**new_user.model_dump(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int = Path(..., ge=1)):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'deleted success'}


@app.get("/products/", response_model=List[Product])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)


@app.post('/products/', response_model=Product)
async def add_product(new_product: Product):
    query = products.insert().values(**new_product.model_dump())
    last_record_id = await database.execute(query)
    return {**new_product.model_dump(), "id": last_record_id}


@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int = Path(..., ge=1)):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)


@app.put("/products/{product_id}", response_model=Product)
async def update_product(new_product: Product, product_id: int = Path(..., ge=1)):
    new_product.id = product_id
    query = products.update().where(products.c.id == product_id).values(**new_product.model_dump())
    await database.execute(query)
    return {**new_product.model_dump()}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int = Path(..., ge=1)):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': 'deleted success'}


@app.post('/incountbalanse/')
async def add_balans_product(add_balans: IncountBalanse):
    query = products_balance.insert().values(**add_balans.model_dump())
    await database.execute(query)
    return {'message:' 'success'}


@app.get("/orders/")
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.post("/orders/")
async def add_order(new_order: Order):
    transaction = await database.transaction()
    await transaction.start()
    try:
        # добавляем заказ
        query = orders.insert().values(user_id=new_order.user_id, )
        last_record_id = await database.execute(query)
        # Добавляем строки заказа
        value_items = []
        for item in new_order.items:
            dict = vars(item)
            dict['order_id'] = last_record_id
            value_items.append(dict)
        query = order_items.insert(value_items)
        await database.execute(query)
        # уменьшаем количество товара на складе
        value_items = []
        all_product_id = []
        for item in new_order.items:
            value_items.append({'product_id': item.product_id, 'quantity': -item.quantity})
            all_product_id.append(item.product_id)
        query = products_balance.insert().values(value_items)
        await database.execute(query)
        # проверяем остатки
        query = products_balance.select().where(products_balance.c.product_id.in_(all_product_id)) \
            .group_by(products_balance.c.product_id) \
            .having(func.sum(products_balance.c.quantity) < 0)
        rs = await database.fetch_one(query)

        if rs:
            for el in rs:
                raise (f'Не хватает количества {el}')

        await transaction.commit()
    except Exception as e:
        await transaction.rollback()
        return {"error": str(e)}

    return {**new_order.model_dump(), "id": last_record_id}


if __name__ == "__main__":
    uvicorn.run("task1:app", port=8000)
