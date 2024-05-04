from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from saleapp.models import Category, Product, UserRole
from saleapp import app, db, dao
from flask_login import logout_user, current_user
from flask import redirect, request
from datetime import datetime


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class MyProductView(AuthenticatedView):
    column_list = ['id', 'name', 'category_id']
    column_searchable_list = ['id', 'name']
    column_filters = ['id', 'name', 'price']
    column_editable_list = ['name', 'price']
    can_export = True
    column_labels = {
        'name': 'Tên sản phẩm',
        'category_id': 'Danh mục'
    }


class MyCategoryView(AuthenticatedView):
    column_list = ['id', 'name', 'products']


class StatsView(BaseView):
    @expose('/')
    def index(self):
        revenue_by_prods = dao.stats_revenue_by_product(kw=request.args.get('kw'))
        revenue_by_period = dao.stats_revenue_by_period(year=request.args.get('year', datetime.now().year),
                                                        period=request.args.get('period', 'month'))

        return self.render('admin/stats.html',
                           revenue_by_prods=revenue_by_prods,
                           revenue_by_period=revenue_by_period)

    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        stats = dao.count_products_by_cate()
        return self.render('admin/index.html', stats=stats)


admin = Admin(app, name='E-commerce Website', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(MyCategoryView(Category, db.session))
admin.add_view(MyProductView(Product, db.session))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
