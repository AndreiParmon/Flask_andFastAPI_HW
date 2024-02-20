from datetime import datetime
import databases
import sqlalchemy
from fastapi.templating import Jinja2Templates
import pandas as pd
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from fastapi import Request, FastAPI

DATABASE_URL = "sqlite:///store.db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI()
templates = Jinja2Templates(directory='./lesson_6_seminar/templates')

# -------------------------------------------------------------------------------------------

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(40)),
    sqlalchemy.Column("last_name", sqlalchemy.String(40)),
    sqlalchemy.Column("email", sqlalchemy.String(100)),
    sqlalchemy.Column("password", sqlalchemy.String(40)),
)

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(80)),
    sqlalchemy.Column("description", sqlalchemy.String(512)),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False),
    sqlalchemy.Column("product_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'), nullable=False),
    sqlalchemy.Column("date", sqlalchemy.String(64), nullable=False,
                      default=datetime.now().strftime("%d/%m/%y, %H:%M:%S"),
                      onupdate=datetime.now().strftime("%d/%m/%y, %H:%M:%S")),
    sqlalchemy.Column("status", sqlalchemy.String(8), nullable=False, server_default="Создан"),

)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


# -------------------------------------------------------------------------------------------

class UserIn(BaseModel):
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=40)
    email: str = Field(max_length=100)
    password: str = Field(min_length=8)


class User(BaseModel):
    id: int
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=40)
    email: str = Field(max_length=100)
    password: str = Field(min_length=8)


class ProductIn(BaseModel):
    title: str = Field(max_length=40)
    description: str = Field(max_length=250)
    price: float = Field(gt=0, le=999999)


class Product(BaseModel):
    id: int
    title: str = Field(max_length=40)
    description: str = Field(max_length=250)
    price: float = Field(gt=0, le=999999)


class OrderIn(BaseModel):
    status: str = Field(default="Создан")


class Order(BaseModel):
    id: int
    date: str
    status: str = Field(default="Создан")
    user_id: int = Field(foreign_key=True)
    product_id: int = Field(foreign_key=True)


# -------------------------------------------------------------------------------------------

@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(**user.model_dump())
    record_id = await database.execute(query)
    return {**user.model_dump(), "id": record_id}


@app.get("/users/", response_class=HTMLResponse)
async def read_users(request: Request):
    query = users.select()
    users_table = pd.DataFrame([user for user in await database.fetch_all(query)]).to_html(index=False)
    return templates.TemplateResponse("users.html", {"request": request, "users_table": users_table})


@app.get("/users/{user_id}", response_model=User)
async def read_user(request: Request, user_id: int):
    query = users.select().where(users.c.id == user_id)
    user = pd.DataFrame([i for i in await database.fetch_all(query)]).to_html(index=False)
    return templates.TemplateResponse("users.html", {"request": request, "user": user})


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
    await database.execute(query)
    return {**new_user.model_dump(), "id": user_id}


@app.delete("/users/{user_id}", response_model=User)
async def delete_user(user_id: int):
    removed = users.select().where(users.c.id == user_id)
    query = users.delete().where(users.c.id == user_id)
    result = await database.fetch_one(removed)
    await database.execute(query)
    return result


# -------------------------------------------------------------------------------------------

@app.post("/product/", response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(**product.model_dump())
    record_id = await database.execute(query)
    return {**product.model_dump(), "id": record_id}


@app.get("/product/", response_class=HTMLResponse)
async def read_products(request: Request):
    query = products.select()
    products_table = pd.DataFrame([product for product in await database.fetch_all(query)]).to_html(index=False)
    return templates.TemplateResponse("products.html", {"request": request, "products_table": products_table})


@app.get("/product/{product_id}", response_model=Product)
async def read_product(request: Request, product_id: int):
    query = products.select().where(products.c.id == product_id)
    product = pd.DataFrame([i for i in await database.fetch_all(query)]).to_html(index=False)
    return templates.TemplateResponse("products.html", {"request": request, "product": product})


@app.put("/product/{product_id}", response_model=Product)
async def update_product(product_id: int, new_product: ProductIn):
    query = products.update().where(products.c.id == product_id).values(**new_product.model_dump())
    await database.execute(query)
    return {**new_product.model_dump(), "id": product_id}


@app.delete("/product/{product_id}", response_model=Product)
async def delete_user(product_id: int):
    removed = products.select().where(products.c.id == product_id)
    query = products.delete().where(products.c.id == product_id)
    result = await database.fetch_one(removed)
    await database.execute(query)
    return result


# -------------------------------------------------------------------------------------------

@app.post("/order/{user_id}/{product_id}", response_model=OrderIn)
async def create_order(user_id: int, product_id: int, order: OrderIn):
    query = orders.insert().values(date=datetime.now().strftime("%d/%m/%y, %H:%M:%S"), status=order.status,
                                   user_id=user_id, product_id=product_id)
    record_id = await database.execute(query)
    return {**order.model_dump(), "id": record_id}


@app.get("/order/", response_class=HTMLResponse)
async def read_order(request: Request):
    query = orders.select()
    orders_table = pd.DataFrame([order for order in await database.fetch_all(query)]).to_html(index=False)
    return templates.TemplateResponse("orders.html", {"request": request, "orders_table": orders_table})


@app.get("/order/{order_id}", response_model=Order)
async def update_order(request: Request, order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    order = pd.DataFrame([i for i in await database.fetch_all(query)]).to_html(index=False)
    return templates.TemplateResponse("orders.html", {"request": request, "order": order})


@app.put("/order/{order_id}", response_model=OrderIn)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(date=datetime.now().strftime("%d/%m/%y, %H:%M:%S"),
                                                                  status=new_order.status)
    await database.execute(query)
    return {**new_order.model_dump(), "id": order_id}


@app.delete("/order/{order_id}", response_model=Order)
async def delete_order(order_id: int):
    removed = orders.select().where(orders.c.id == order_id)
    query = orders.delete().where(orders.c.id == order_id)
    result = await database.fetch_one(removed)
    await database.execute(query)
    return result

# -------------------------------------------------------------------------------------------
