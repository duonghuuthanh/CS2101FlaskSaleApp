import math
from flask import render_template, request, redirect, jsonify, session
import dao
import utils
from saleapp import app, login
from saleapp.models import UserRole
from flask_login import login_user, logout_user, login_required
import cloudinary.uploader


@app.route("/")
def index():
    kw = request.args.get('kw')
    cate_id = request.args.get('category_id')
    page = request.args.get('page')

    prods = dao.load_products(kw=kw, cate_id=cate_id, page=page)
    total = dao.count_product()

    return render_template('index.html', products=prods,
                           pages=math.ceil(total/app.config['PAGE_SIZE']))


@app.route('/login', methods=['get', 'post'])
def process_login_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username, password)
        if u:
            login_user(u)

            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không hợp lệ!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/register', methods=['get', 'post'])
def process_register():
    err_msg = None
    if request.method.__eq__('POST'):
        try:
            password = request.form['password']
            confirm = request.form['confirm']

            if password.__eq__(confirm):
                avatar = None
                a = request.files.get('avatar')
                if a:
                    res = cloudinary.uploader.upload(a)
                    avatar = res.get('secure_url')

                try:
                    dao.add_user(username=request.form['username'],
                                 password=password,
                                 name=request.form['name'], avatar=avatar)
                except:
                    err_msg = 'Hệ thống đang có lỗi! Vui lòng quay lại sau!'
                else:
                    return redirect('/login')
            else:
                err_msg = 'Mật khẩu không khớp'
        except:
            err_msg = 'Dữ liệu không hợp lệ!'

    return render_template('register.html', err_msg=err_msg)


@app.route("/logout")
def my_user_logout():
    logout_user()
    return redirect("/")


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password, user_role=UserRole.ADMIN)
    if u:
        login_user(user=u)

    return redirect('/admin')


@login.user_loader
def get_user(id):
    return dao.get_user_by_id(id)


@app.route('/cart')
def cart_view():
    return render_template('cart.html')


@app.route('/api/cart', methods=['post'])
def add_to_cart():
    """
    {
        "1": {
            "id": "1",
            "name": "abc",
            "price": 12,
            "quantity": 2
        }, "2": {
            "id": "2",
            "name": "abc",
            "price": 12,
            "quantity": 1
        }
    }
    :return:
    """
    cart = session.get('cart')
    if not cart:
        cart = {}

    id = str(request.json.get('id'))
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": request.json.get('name'),
            "price": request.json.get('price'),
            "quantity": 1
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        cart[product_id]['quantity'] = int(request.json.get('quantity', 0))
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:
        dao.add_receipt(session.get('cart'))
    except:
        return jsonify({'status': 500})
    else:
        del session['cart']
        return jsonify({'status': 200})


@app.context_processor
def common_attributes():
    return {
        'categories': dao.load_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


if __name__ == '__main__':
    with app.app_context():
        from saleapp import admin
        app.run(debug=True)
