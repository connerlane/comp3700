#!/usr/bin/env python
from db_utils import SQLiteDatabase


class ItemDatabase(SQLiteDatabase):
    def __init__(self):
        super().__init__('item_database.db')

    def get_product(self, product_id):
        return self.get_row('Product', ('id', product_id))

    def get_product_by_name(self, name):
        return self.get_row('Product', ('name', name))

    def product_table(self):
        query = ('SELECT name, id, quantity, price, provider, '
                 '    provider_contact '
                 'FROM Product ORDER BY id')
        return self.fetchall(query)

    def add_new_product(self, item):
        query = ('INSERT INTO Product '
                 '    (name, quantity, price, provider, provider_contact) '
                 'VALUES '
                 '    (:name, :quantity, :price, :provider, :provider_contact)')
        self.execute(query, dict(item))

    def update_product(self, product, product_id):
        """Update a product in the item database.

        :param FormsDict product: Product info form passed in from POST.
        :param int product_id: Primary key used for database lookup.
        """
        self.update_row_from_form(product, 'Product', ('id', product_id))

    def delete_product(self, product_id):
        self.delete_row('Product', ('id', product_id))

    def get_order(self, order_id):
        return self.get_row('"Order"', ('id', order_id))

    def order_table(self):
        return self.get_table('"Order"')

    def add_new_order(self):
        self.add_default_row('"Order"')

    def update_order(self, field, order_id):
        self.update_row('"Order"', field, ('id', order_id))

    def delete_order(self, order_id):
        self.delete_row('"Order"', ('id', order_id))

    def orderline_table(self, order_id):
        query = ('SELECT Product.name, OrderLine.quantity, OrderLine.price,'
                 '    OrderLine.cost '
                 'FROM OrderLine '
                 'JOIN Product ON Product.id = OrderLine.product_id '
                 'WHERE order_id = ? ORDER BY OrderLine.id')
        return self.fetchall(query, (order_id,))

    def add_orderline(self, order_id, product_id, quantity, price, cost):
        self.execute('INSERT INTO OrderLine'
                     '    (order_id, product_id, quantity, price, cost) '
                     'VALUES (?, ?, ?, ?, ?)',
                     (order_id, product_id, quantity, price, cost))

    def add_orderline_from_item(self, item, order_id):
        product_result = self.get_product_by_name(item['name'])
        order_result = self.get_order(order_id)

        if product_result is None:
            # Item not found.
            return False

        product_id = product_result['id']
        price = product_result['price']
        quantity = int(item['quantity'])
        cost = quantity * price

        # Update order total.
        total = order_result['total'] + cost
        self.update_row('"Order"', ('total', total), ('id', order_id))

        # Add order line.
        self.add_orderline(cost, order_id, price, product_id, quantity)

        return True
