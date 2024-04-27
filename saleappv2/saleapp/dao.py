from saleapp.models import Category, Product, User, UserRole
from saleapp import app, db
import hashlib


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


if __name__ == '__main__':
    print(load_categories())
