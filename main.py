from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

API_KEY = "TopSecretAPIKey"

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
         # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        
        # #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/report-closed/<int:id>', methods=['DELETE'])
def delete_cafe_data(id):
    user_key = request.args.get("api-key")
    if user_key == API_KEY:
        cafe = db.get_or_404(Cafe, id)
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"success":"cafe data is successfully deleted"}), 200
    else:
        return jsonify(response={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
    
@app.route('/update-price/<int:id>', methods=['PATCH'])
def update_coffee_price(id):
    cafe = db.get_or_404(Cafe, id)
    new_price = request.args.get("new_price")
    print(new_price)
    if not cafe:
        return jsonify(error="Missing or Invalid JSON data"), 400
    # Update only the price field
    cafe.coffee_price = new_price
    db.session.commit()
    return jsonify(response={"success":"Database 'Cafe' is successfully updated"})


@app.route('/add', methods=['POST'])
def add_new_cafe():
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        seats = request.form.get("seats"),
        has_toilet = bool(request.form.get("has_toilet")),
        has_wifi = bool(request.form.get("has_wifi")),
        has_sockets = bool(request.form.get("has_sockets")),
        can_take_calls = bool(request.form.get("can_take_calls")),
        coffee_price = request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route('/all', methods=['GET'])
def get_all():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafes = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafe=cafes)

@app.route('/search', methods=['GET'])
def search_cafe():
    location = request.args.get('loc')
    if not location:
        return jsonify({"error": "Please provide a location parameter"})
    searching_cafes = db.session.execute(db.select(Cafe).where(Cafe.location == location)).scalars().all()
    if not searching_cafes:
        return jsonify({"error": f"No cafes found in {location}"})
    searched_cafes = [cafe.to_dict() for cafe in searching_cafes]
    return jsonify(cafe=searched_cafes)

@app.route('/random', methods=['GET'])
def get_random_cafe():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())

    # return jsonify(cafe={
    #         "id":random_cafe.id,
    #         "name":random_cafe.name,
    #         "map_url":random_cafe.map_url,
    #         "img_url":random_cafe.img_url,
    #         "location":random_cafe.location,
    #         "has_sockets":random_cafe.has_sockets,
    #         "has_sockets":random_cafe.has_sockets,
    #         "has_toilet":random_cafe.has_toilet,
    #         "has_wifi":random_cafe.has_wifi,
    #         "can_take_calls":random_cafe.can_take_calls,
    #         "seats":random_cafe.seats,
    #         "coffee_price":random_cafe.coffee_price
    #     })

    # return jsonify(cafe={
    #     #Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
        
    #     #Put some properties in a sub-category
    #     "amenities": {
    #       "seats": random_cafe.seats,
    #       "has_toilet": random_cafe.has_toilet,
    #       "has_wifi": random_cafe.has_wifi,
    #       "has_sockets": random_cafe.has_sockets,
    #       "can_take_calls": random_cafe.can_take_calls,
    #       "coffee_price": random_cafe.coffee_price,
    #     }
    # })



# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
