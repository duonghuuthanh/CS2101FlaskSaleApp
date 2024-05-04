import math
from flask import render_template, request, redirect, session, jsonify
import dao
import utils
from saleapp import app, login
from flask_login import login_user, logout_user, login_required
import cloudinary.uploader
from decorators import loggedin


@app.route('/')
def index():
    q = request.args.get('q')
    cate_id = request.args.get('category_id')
    page = request.args.get('page')

    products = dao.load_products(q=q, cate_id=cate_id, page=page)
    return render_template('index.html', products=products,
                           pages=math.ceil(dao.count_product()/app.config['PAGE_SIZE']))


@app.route('/products/<int:id>')
def details(id):
    product = dao.get_product_by_id(product_id=id)
    comments = dao.get_comments(product_id=id)
    return render_template('product-details.html', product=product, comments=comments)


@app.route('/login', methods=['get', 'post'])
@loggedin
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            err_msg = 'Username hoặc password không đúng!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/logout', methods=['get'])
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route("/admin-login", methods=['post'])
def process_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)

    return redirect('/admin')


@app.route('/register', methods=['get', 'post'])
@loggedin
def register_user():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            avatar_path = None
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']

            dao.add_user(name=request.form.get('name'),
                         username=request.form.get('username'),
                         password=password,
                         avatar=avatar_path)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)


@app.route('/api/carts', methods=['post'])
def add_to_cart():
    """
    {
        "cart": {
            "1": {
                "id": "",
                "name": "...",
                "price": "...",
                "quantity": 2
            }, "2": {
                "name": "...",
                "price": "...",
                "quantity": 1
            }
        }
    }
    :return:
    """
    cart = session.get('cart')
    if not cart:
        cart = {}

    id = str(request.json.get('id'))
    if id in cart:
        cart[id]["quantity"] += 1
    else:
        cart[id] = {
            "id": id,
            "name": request.json.get("name"),
            "price": request.json.get("price"),
            "quantity": 1
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/api/cart/<product_id>', methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        cart[product_id]['quantity'] = request.json['quantity']
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route("/api/pay", methods=['post'])
@login_required
def pay():
    cart = session.get('cart')
    try:
        dao.add_receipt(cart)
    except Exception as ex:
        print(ex)
        return jsonify({'status': 500})
    else:
        del session['cart']
        return jsonify({'status': 200})


@app.route('/api/products/<int:id>/comments', methods=['post'])
@login_required
def add_comment(id):
    data = request.json
    c = dao.add_comment(content=data.get('content'), product_id=id)

    return jsonify({'id': c.id, 'content': c.content, 'user': {
        'username': c.user.username,
        'avatar': c.user.avatar
    }})


@app.context_processor
def common_attributes():
    return {
        'categories': dao.load_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from saleapp import admin
        app.run(debug=True)
