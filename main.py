from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

# # Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mtl_cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# # Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    has_toilet = db.Column(db.Boolean, nullable=True)
    has_wifi = db.Column(db.Boolean, nullable=True)
    has_sockets = db.Column(db.Boolean, nullable=True)
    can_take_calls = db.Column(db.Boolean, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

# # HTTP GET - Read Record
@app.route("/all", methods=['GET'])
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    dictionary = {'cafes': []}
    for cafe in all_cafes:
        new_entry = cafe.to_dict()
        dictionary['cafes'].append(new_entry)
    return jsonify(dictionary)


@app.route("/random", methods=['GET'])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/search")
def search_cafe():
    location = request.args.get('loc').title()
    cafe = Cafe.query.filter_by(location=location).all()
    if cafe:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafe])
    else:
        return jsonify(error={"Not Found": f"Sorry, we don/'t have a cafe at {location}."})


# # HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':

        new_cafe = Cafe(name=request.form.get("name"),
                        seats=request.form.get("seats"),
                        location=request.form.get("location"),
                        map_url=request.form.get("map_url"),
                        img_url=request.form.get("img_url"),
                        has_toilet=bool(request.form.get("has_toilet")),
                        has_wifi=bool(request.form.get("has_wifi")),
                        has_sockets=bool(request.form.get("has_sockets")),
                        can_take_calls=bool(request.form.get("can_take_calls")),
                        coffee_price=request.form.get("coffee_price"))
        db.session.add(new_cafe)
        db.session.commit()

        return jsonify(response={"Success": "Successfully added new cafe."})
    else:
        return render_template('add.html')


# # HTTP PUT/PATCH - Update Record
@app.route("/update_price/<cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get('new_price')
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": f"{cafe_to_update.name} price updated to {new_price}."}), 200
    else:
        return jsonify(error={"Not Found": "Cafe not found in database."}), 404


# # HTTP DELETE - Delete Record
@app.route("/delete/<cafe_id>", methods=['DELETE'])
def report_closed(cafe_id):
    api_key = request.args.get('api_key')
    if api_key == 'TopSecretAPIKey':
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"Success": f"{cafe_to_delete.name} has been deleted from database."}), 200
        else:
            return jsonify(error={"Not Found": "Cafe not found in database."}), 404
    else:
        return jsonify(error={"Authentication": "Valid API key required to report closure."}), 403


if __name__ == '__main__':
    app.run(debug=True)
