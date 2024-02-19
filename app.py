from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

from flask_bcrypt import Bcrypt

from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://ecommerce_db_dev_1:123456@localhost:5432/ecommerce_db"
app.config["JWT_SECRET_KEY"] = "secret"

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class Product(db.Model):
  __tablename__ = "products"
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(50), nullable = False)
  description = db.Column(db.String(100))
  price = db.Column(db.Float)
  stock = db.Column(db.Integer)

class Product_Schema(ma.Schema):
  class Meta:
    fields = ("id","name","description","price","stock")

products_schema = Product_Schema(many=True)
product_schema = Product_Schema()

@app.cli.command("create")
def create_tables():
  db.create_all()
  print("Tables created")

@app.cli.command("seed")
def seed_db():
  product1 = Product()
  product1.name = "Product 1"
  product1.description = "This product is for something"
  product1.price = 400.99
  product1.stock = 100

  product2 = Product()
  product2.name = "Product 2"
  product2.description = "This product is for something"
  product2.price = 200.99
  product2.stock = 200

  db.session.add(product1)
  db.session.add(product2)
  db.session.commit()
  print("Table seeded")

@app.cli.command("drop")
def drop_tables():
  db.drop_all()
  print("tables_dropped")

@app.route("/products")
def get_product():
  stmt = db.select(Product)
  product_list = db.session.scalars(stmt)
  data = products_schema.dump(product_list)
  return data

@app.route("/products/<int:product_id>")
def get_one_product(product_id):
  stmt = db.select(Product).filter_by(id=product_id)
  product = db.session.scalar(stmt)
  if product:
    data = product_schema.dump(product)
    return data
  else:
    return {"Error":f"The id {product_id} does not exist."}

@app.route("/products", methods=["POST"])
def add_product():
  product_fields = request.get_json()
  new_product = Product(
    name=product_fields.get("name"),
    description = product_fields.get("description"),
    price = product_fields.get("price"),
    stock = product_fields.get("stock")
  )
  db.session.add(new_product)
  db.session.commit()
  data = product_schema.dump(product_fields)
  return data, 201

@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
  stmt = db.select(Product).filter_by(id=product_id)
  product = db.session.scalar(stmt)
  product_fields = request.get_json()
  if product:
    product.name = product_fields.get("name") or product.name
    product.description = product_fields.get("description") or product.description
    product.price = product_fields.get("price") or product.price
    product.stock = product_fields.get("stock") or product.stock
    db.session.commit()
    return product_schema.dump(product)
  else:
    return {"error":f"The product with id{product_id} does not exits"}, 404

@app.route("/products/<int:product_id>", methods = ["DELETE"])
def delete_product(product_id):
  stmt = db.select(Product).filter_by(id=product_id)
  product = db.session.scalar(stmt)
  if product:
    db.session.delete(product)
    db.session.commit()
    return {"Msg":f"Product with {product_id} has been deleted."}
  else:
    return {"error":f"Product with {product_id} does not exist."}