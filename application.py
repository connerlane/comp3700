#!/usr/bin/env python
import bottle
from bottle import template, static_file, view, redirect, request, post

import db_utils

app = bottle.Bottle()


@app.route('/', name='index')
def index():
    return template('index')


@app.route('/orders', name='order_list')
def order_list():
    table = db_utils.order_table()
    new_id = table[0][0] + 1
    return template('orders', table=table, new_id=new_id)


@app.route('/order/<order_id:int>', name='order_receipt')
def order_receipt(order_id):
    table = db_utils.orderline_table(order_id)
    return template('order', table=table, order_id=order_id)


@app.get('/add/order/<order_id:int>', name='add_order')
@app.post('/add/order/<order_id:int>')
def add_order(order_id):
    if not db_utils.get_order(order_id):
        # Create order if it does not exist.
        db_utils.add_order()
    if request.method == 'POST':
        # Add item to order.
        result = db_utils.add_orderline(request.forms, order_id)
        return template('add-order', added=result, order_id=order_id,
                        item=request.forms)
    return template('add-order', order_id=order_id)


@app.get('/add/product', name='add_product')
@app.post('/add/product')
def add_product():
    if request.method == 'POST':
        db_utils.add_new_product(request.forms)
        redirect(app.get_url('product_list'))
    return template('add')


@app.route('/products', name='product_list')
def product_list():
    table = db_utils.product_table()
    return template('products', table=table)


@app.get('/update/<product_id:int>', name='update_product')
@app.post('/update/<product_id:int>')
def update_product(product_id):
    if request.method == 'POST':
        db_utils.update_product(request.forms, product_id)
        redirect(app.get_url('product_list'))
    data = db_utils.get_product(product_id)
    return template('update', item_data=data)


@app.get('/delete/<product_id:int>', name='delete_product')
def delete_product(product_id):
    db_utils.delete_product(product_id)
    redirect(app.get_url('product_list'))


@app.route("/static/<file:path>")
def send_static(file):
    return static_file(file, root='static/')


if __name__ == "__main__":
    app.run(debug=True, port=8080, reloader=True)
