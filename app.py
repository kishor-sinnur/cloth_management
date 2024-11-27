from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)  # New field for description
    image_url = db.Column(db.String(300), nullable=True)  # New field for image URL

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

def seed_books():
    if not Book.query.first():
        dummy_books = [
            Book(
                title="To Kill a Mockingbird",
                author="Harper Lee",
                price=299.99,
                description="A classic novel of racism and injustice in the American South.",
                image_url="../static/images/1.jpg"
            ),
            Book(
                title="1984",
                author="George Orwell",
                price=199.99,
                description="A dystopian novel about totalitarianism and surveillance.",
                image_url="../static/images/2.jpg"
            ),
            Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                price=249.99,
                description="A tragic love story set in the Jazz Age.",
                image_url="../static/images/3.jpg"
            ),
        ]
        db.session.bulk_save_objects(dummy_books)
        db.session.commit()


@app.before_request
def setup():
    db.create_all()
    seed_books()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400
    hashed_password = data['password']
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and data['password']:
        return jsonify({"user_id": user.id}), 200
    return jsonify({"message": "Invalid credentials"}), 401
@app.route('/addbooks', methods=['POST'])
def add_book():
    data = request.form
    image_url = data.get('image_url')  # Use the relative URL provided by Perl script

    new_book = Book(
        title=data.get('title'),
        author=data.get('author'),
        price=data.get('price'),
        description=data.get('description'),
        image_url=image_url  # Save the relative URL to the database
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully"}), 201


@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "description": book.description,  # Include description
        "image_url": book.image_url  # Include image URL
    } for book in books])

@app.route('/cart', methods=['GET', 'POST', 'DELETE'])
def manage_cart():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    if request.method == 'POST':
        data = request.json
        if not data or not data.get('book_id'):
            return jsonify({"message": "Book ID is required"}), 400

        book = Book.query.get(data['book_id'])
        if not book:
            return jsonify({"message": "Book not found"}), 404

        try:
            cart_item = Cart(user_id=user_id, book_id=data['book_id'])
            db.session.add(cart_item)
            db.session.commit()
            return jsonify({"message": "Book added to cart"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error: {str(e)}"}), 500

    elif request.method == 'DELETE':
        data = request.json
        if not data or not data.get('book_id'):
            return jsonify({"message": "Book ID is required"}), 400

        cart_item = Cart.query.filter_by(user_id=user_id, book_id=data['book_id']).first()
        if cart_item:
            try:
                db.session.delete(cart_item)
                db.session.commit()
                return jsonify({"message": "Book removed from cart"}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": f"Error: {str(e)}"}), 500

        return jsonify({"message": "Cart item not found"}), 404

    else:  # GET method
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "book_id": item.book_id,
            "title": Book.query.get(item.book_id).title,
            "price": Book.query.get(item.book_id).price,
            "description": Book.query.get(item.book_id).description,
            "image_url": Book.query.get(item.book_id).image_url
        } for item in cart_items])



if __name__ == '__main__':
    app.run(debug=True)

