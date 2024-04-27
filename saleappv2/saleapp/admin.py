from saleapp import app, db
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from saleapp.models import Category, Product, UserRole
from flask import redirect
from flask_login import logout_user, current_user
import dao

admin = Admin(app, name='eCommerce Website', template_mode='bootstrap4')


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class CategoryView(AdminView):
    column_list = ['id', 'name', 'products']


class ProductView(AdminView):
    column_list = ['id', 'name', 'price', 'active']
    can_export = True
    column_sortable_list = ['id', 'name']
    column_searchable_list = ['id', 'name']
    column_editable_list = ['name', 'price', 'active']
    column_filters = ['id', 'price', 'name']


class StatsView(MyView):
    @expose('/')
    def index(self):
        data = dao.stats_revenue()
        return self.render('admin/stats.html', stats_data=data)


class LogoutView(MyView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(CategoryView(Category, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))