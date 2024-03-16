from flask import Flask, render_template, request, redirect
import dao

app = Flask(__name__)


@app.route("/")
def index():
    kw = request.args.get('kw')
    cate_id = request.args.get('category_id')

    prods = dao.load_products(kw=kw, cate_id=cate_id)
    return render_template('index.html', products=prods)


@app.route('/login', methods=['get', 'post'])
def process_login_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        if username.__eq__('admin') and password.__eq__('123'):
            return redirect('/')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không hợp lệ!'

    return render_template('login.html', err_msg=err_msg)


@app.context_processor
def common_attributes():
    return {
        'categories': dao.load_categories()
    }


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
