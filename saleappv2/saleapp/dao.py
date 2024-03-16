import json


def load_categories():
    with open('data/categories.json', encoding='utf-8') as f:
        return json.load(f)


def load_products(kw=None, cate_id=None):
    with open('data/products.json', encoding='utf-8') as f:
        products = json.load(f)

        if kw:
            products = [p for p in products if p['name'].find(kw) >= 0]

        if cate_id:
            products = [p for p in products if p['category_id'] == int(cate_id)]

        return products


if __name__ == '__main__':
    print(load_categories())
