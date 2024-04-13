from saleapp.models import Category, Product
from saleapp import app


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


if __name__ == '__main__':
    print(load_categories())
