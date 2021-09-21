from app import app, db
from flask import (render_template, request, redirect, url_for, session,
                   flash, Blueprint, abort
                   )

from flask_login import current_user, login_required

from app.models import Inversionistas, Organizaciones, Products, Kart, Eventos
from app.admin.forms import Variations
import random
home = Blueprint('home', __name__)


@home.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    # preventing non admins from accessing the page
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/admin_dashboard.html', title="Dashboard")


@home.route('/', methods=['GET'])
def landing():
    return redirect(url_for("home.homepage"))


@home.route('/home', methods=['GET'])
def homepage():
    products = Products.query.all()

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    return render_template("home/index.html", title='Website name',
                           products=products, count=count, len=len(products))


@home.route('/canasta')
def canasta():
    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    page = request.args.get('page', 1, type=int)

    products = Products.query\
        .order_by(Products.product_name).paginate(page=page, per_page=6)

    return render_template("home/canasta.html", title="Canasta Agricola", products=products, count=count)


@home.route('/organizaciones')
def organizaciones():

    page = request.args.get('page', 1, type=int)

    organizaciones = Organizaciones.query\
        .order_by(Organizaciones.organizacion_name).paginate(page=page, per_page=6)

    return render_template("home/organizaciones.html", title="Organizaciones", organizaciones=organizaciones)


@home.route('/organizaciones/<string:organizacion_name>', methods=["GET", "POST"])
def organizacion_details(organizacion_name):

    organizacion = Organizaciones.query.filter_by(
        organizacion_name=organizacion_name).first_or_404()

    return render_template("home/organizacion_details.html",
                           organizacion=organizacion, title=organizacion.organizacion_name)


@home.route('/product/<int:id>', methods=["GET", "POST"])
def product_details(id):
    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()
        user = current_user.id

    form = Variations()

    product_detail = Products.query.filter_by(id=id).first_or_404()
    organizacion = Organizaciones.query.filter_by(id=product_detail.organizacion_id).first_or_404()

    # add to cart
    if form.validate_on_submit():
        # annonymous users
        if current_user.is_anonymous:
            flash(
                'Please login before you can add items to your shopping cart', 'warning')
            return redirect(url_for("home.product_details", id=product_detail.id))
        # authenticated users
        cart = Kart(user_id=user, product_id=product_detail.id,
                    quantity=form.amount.data, subtotal=product_detail.product_price)
        db.session.add(cart)
        db.session.commit()

        flash(f"{product_detail.product_name} has been added to cart")
        return redirect(url_for('home.product_details', id=product_detail.id))
    return render_template("home/productdetails.html",
                           product_detail=product_detail, title=product_detail.product_name,
                           form=form, count=count, organizacion=organizacion)


@home.route('/inversionistas')
def inversionistas():

    page = request.args.get('page', 1, type=int)

    inversionistas = Inversionistas.query\
        .order_by(Inversionistas.inversionista_name).paginate(page=page, per_page=6)

    return render_template("home/inversionistas.html", title="Inversionistas", inversionistas=inversionistas)


@home.route('/inversionistas/<int:inversionista_id>', methods=["GET", "POST"])
def inversionista_details(inversionista_id):

    inversionista = Inversionistas.query.filter_by(
        id=inversionista_id).first_or_404()

    return render_template("home/inversionista_details.html",
                           inversionista=inversionista, title=inversionista.inversionista_name)


@home.route('/eventos')
def eventos():
    eventos = Eventos.query.all()
    return render_template("home/eventos.html", title="Eventos", eventos=eventos)
