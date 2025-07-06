from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Email
import sqlite3
import os


app = Flask(__name__)
app.secret_key = 'secret-key'
DB = 'furniture.db'


# ------------------ Flask-WTF Order Form ------------------ #
class OrderForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    phone = StringField("Phone", validators=[InputRequired()])
    address = TextAreaField("Address", validators=[InputRequired()])


# ------------------ Database Connection ------------------ #
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/create_db')
def create_db():
    conn = get_db()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, type TEXT, material TEXT,
            price REAL, image TEXT, desc TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT,
            address TEXT, items TEXT, total REAL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    products = [
        # --- Chairs ---
        ("Wood Chair 1", "Chair", "Wood", 100, "wood_chair1.jpg", "Classic wooden chair"),
        ("Wood Chair 2", "Chair", "Wood", 110, "wood_chair2.jpg", "Modern wooden chair"),
        ("Wood Chair 3", "Chair", "Wood", 120, "wood_chair3.jpg", "Elegant wooden chair"),
        ("Plastic Chair 1", "Chair", "Plastic", 90, "plastic_chair1.jpg", "Red plastic chair"),
        ("Plastic Chair 2", "Chair", "Plastic", 95, "plastic_chair2.jpg", "Simple plastic chair"),

        # --- Sofas ---
        ("Fabric Sofa", "Sofa", "Fabric", 420, "sofa1.jpg", "Premium fabric sofa"),
        ("Sofa Leather", "Sofa", "Leather", 400, "sofa2.jpg", "Comfortable leather sofa"),
        ("Sofa 3", "Sofa", "Leather", 450, "sofa3.jpg", "Royal leather sofa"),
        ("Sofa 4", "Sofa", "Fabric", 470, "sofa4.jpg", "Modern luxury fabric sofa"),
        ("Sofa 5", "Sofa", "Wood", 490, "sofa5.jpg", "Wooden base premium sofa"),

        # --- Tables ---
        ("Wood Table 1", "Table", "Wood", 220, "wood_table1.jpg", "Strong wooden table"),
        ("Glass Table", "Table", "Glass", 300, "glass_diningtable.jpg", "Elegant glass table"),

        # --- Beds ---
        ("Wood Bed 1", "Bed", "Wood", 600, "wood_bed1.jpg", "Luxury king-size wooden bed"),
        ("Wood Bed 2", "Bed", "Wood", 650, "wood_bed2.jpg", "Classic wooden bed with drawers"),

        # --- Mattress ---
        ("Soft Mattress", "Mattress", "Foam", 350, "mattress1.jpg", "Memory foam mattress"),
        ("Soft Mattress 2", "Mattress", "Foam", 370, "mattress2.jpg", "Premium memory mattress"),

        # --- Lighting ---
        ("Lamp Lighting 1", "Lighting", "Metal", 200, "lamp1.jpg", "Stylish table lamp"),
        ("Lamp Lighting 2", "Lighting", "Metal", 220, "lamp2.jpg", "Hanging lamp with warm light"),
        ("Lamp Lighting 3", "Lighting", "Wood", 240, "lamp3.jpg", "Designer wooden lamp"),

        # --- Decor ---
        ("Wall Decor Art", "Decor", "Canvas", 150, "decor1.jpg", "Modern wall art decor"),
        ("Wall Decor 2", "Decor", "Wood", 210, "decor2.jpg", "Wooden frame wall decor"),

        # --- Rooms ---
        ("Living Room Set", "Room", "Wood", 1200, "room1.jpg", "Luxury living room setup with sofa and table"),
        ("Bedroom Combo", "Room", "Wood", 1500, "room2.jpg", "Modern bedroom set with bed and wardrobes"),

    ]

    conn.executemany('''
        INSERT INTO products (name, type, material, price, image, desc)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', products)

    conn.commit()
    conn.close()
    return "✅ Database created and 22 sample products inserted."

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        existing = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            flash("User already exists. Please login.", "warning")
            return redirect(url_for('login'))

        conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()

        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html', title="Signup")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not user:
            flash("No account found. Please signup first.", "danger")
            return redirect(url_for('signup'))

        if user['password'] == password:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        else:
            flash("Incorrect password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html', title="Login")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ------------------ Home Page ------------------ #
@app.route('/')
def home():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()

    categories = [
        {"name": "Sofas", "image": "sofa_category.jpg"},
        {"name": "Chairs", "image": "chair_category.jpg"},
        {"name": "Tables", "image": "table_category.jpg"},
        {"name": "Beds", "image": "bed_category.jpg"},
        {"name": "Mattress", "image": "mattress_category.jpg"},
        {"name": "Lighting", "image": "lighting_category.jpg"},
        {"name": "Rooms", "image": "room_category.jpg"},
        {"name": "Decor", "image": "decor_category.jpg"},
    ]

    return render_template("home.html", products=products, categories=categories)

@app.route('/search')
def search():
    query = request.args.get('search')
    db = get_db()

    if query:
        products = db.execute("SELECT * FROM products WHERE LOWER(name) LIKE ? OR LOWER(desc) LIKE ?", 
                              (f"%{query.lower()}%", f"%{query.lower()}%")).fetchall()
    else:
        products = []

    return render_template("search.html", products=products)




# ------------------ Product Detail Page ------------------ #
@app.route('/product/<int:id>')
def product(id):
    db = get_db()
    prod = db.execute('SELECT * FROM products WHERE id=?', (id,)).fetchone()
    related = db.execute('SELECT * FROM products WHERE type=? AND id!=? LIMIT 3', (prod['type'], id)).fetchall()
    return render_template("product.html", product=prod, related=related)


# ------------------ Add to Cart ------------------ #
@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not product:
        flash("❌ Product not found!")
        return redirect(url_for('home'))

    qty = int(request.form.get('qty', 1))
    session.setdefault('cart', [])
    for _ in range(qty):
        session['cart'].append(id)

    flash("✅ Product added to cart!")
    return redirect(url_for('cart'))



# ------------------ Cart Page ------------------ #
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    db = get_db()
    item_counts = {}

    for pid in cart:
        item_counts[pid] = item_counts.get(pid, 0) + 1

    items, total = [], 0
    for pid, qty in item_counts.items():
        item = db.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        item_dict = dict(item)
        item_dict['qty'] = qty
        item_dict['subtotal'] = item['price'] * qty
        items.append(item_dict)
        total += item_dict['subtotal']

    return render_template("cart.html", items=items, total=total)


# ------------------ Order Page with Manual Form ------------------ #
@app.route('/place-order', methods=['GET', 'POST'])
def place_order():
    cart = session.get('cart', [])
    db = get_db()
    item_counts, items, total = {}, [], 0

    for pid in cart:
        item_counts[pid] = item_counts.get(pid, 0) + 1

    for pid, qty in item_counts.items():
        item = db.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        item_dict = dict(item)
        item_dict['qty'] = qty
        item_dict['subtotal'] = item['price'] * qty
        items.append(item_dict)
        total += item_dict['subtotal']

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        print(f"Order from {name}, Phone: {phone}, Address: {address}, Total: Rs{total}")
        session['cart'] = []
        return redirect(url_for('order_success'))

    return render_template("order.html", items=items, total=total, form=None)


# ------------------ Order Page using Flask-WTF ------------------ #
@app.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    cart = session.get('cart', [])
    db = get_db()
    item_counts, items, total = {}, [], 0

    for pid in cart:
        item_counts[pid] = item_counts.get(pid, 0) + 1

    for pid, qty in item_counts.items():
        item = db.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        items.append(f"{item['name']} x{qty}")
        total += item['price'] * qty

    if form.validate_on_submit():
        db.execute('''
            INSERT INTO orders (name, email, phone, address, items, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (form.name.data, form.email.data, form.phone.data, form.address.data, ', '.join(items), total))
        db.commit()
        session['cart'] = []
        return render_template("order_success.html", name=form.name.data)

    return render_template("order.html", form=form, items=items, total=total)


# ------------------ Order Success ------------------ #
@app.route('/order-success')
def order_success():
    return render_template("order_success.html")


# ------------------ Static Pages ------------------ #
@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_sent = False
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        msg = request.form.get('message')
        print(f"Message from {name} ({email}): {msg}")
        message_sent = True
    return render_template("contact.html", message_sent=message_sent)


@app.route('/new-arrival')
def new_arrival():
    db = get_db()
    products = db.execute('SELECT * FROM products ORDER BY id DESC LIMIT 6').fetchall()
    return render_template("new_arrival.html", products=products)


@app.route('/partners')
def partners():
    members = [
        {"name": "Ayushman Patnaik", "role": "Frontend Designer"},
        {"name": "Subham Panigrahy", "role": "Backend Developer"},
        {"name": "Chandra Sekhar Sahu", "role": "System Designer"},
        {"name": "K.Ajay kumar", "role": "Database Manager"},
        {"name": "Asutosh Patra", "role": "Testing & Documentation"},
    ]
    return render_template("partners.html", members=members)


@app.route('/category/<category_name>')
def category(category_name):
    db = get_db()

    # Normalize category (e.g., 'sofa' → 'Sofa')
    normalized = category_name.capitalize()

    products = db.execute(
        "SELECT * FROM products WHERE LOWER(type) = ?",
        (normalized.lower(),)
    ).fetchall()

    if products:
        return render_template("category_view.html", category=normalized, products=products)
    else:
        return f"<h2>❌ No products found in category '{category_name}'</h2>", 404

@app.route('/shop')
def shop():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("shop.html", products=products)




# ------------------ Run Flask App ------------------ #
if __name__ == '__main__':
    app.run(debug=True)