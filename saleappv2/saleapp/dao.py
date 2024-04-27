from saleapp.models import Category, Product, User, UserRole, Receipt, ReceiptDetails
from saleapp import app, db
import hashlib
from flask_login import current_user
from sqlalchemy import func


def load_categories():
    return Category.query.order_by(Category.name).all()


def load_products(kw=None, cate_id=None, page=None):
    query = Product.query

    if kw:
        query = query.filter(Product.name.contains(kw))

    if cate_id:
        query = query.filter(Product.category_id.__eq__(cate_id))

    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        return query.slice(start, start + page_size).all()
    else:
        return query.all()


def count_product():
    return Product.query.count()


def auth_user(username, password, user_role=UserRole.USER):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(user_role)).first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name.strip(), username=username.strip(),
             password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(id):
    return User.query.get(id)


def add_receipt(cart):
    if cart:
        r = Receipt(user=current_user)
        db.session.add(r)

        for d in cart.values():
            detail = ReceiptDetails(quantity=d['quantity'],
                                    unit_price=d['price'],
                                    receipt=r,
                                    product_id=d['id'])
            db.session.add(detail)

        db.session.commit()


def stats_revenue():
    query = db.session.query(Product.id, Product.name, func.sum(ReceiptDetails.quantity*ReceiptDetails.unit_price))\
              .join(ReceiptDetails, ReceiptDetails.product_id.__eq__(Product.id), isouter=True).group_by(Product.id)

    return query.all()


if __name__ == '__main__':
    with app.app_context():
        print(stats_revenue())
