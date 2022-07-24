from sqlalchemy import and_, or_, not_
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import desc, func, cast, Numeric, text
from models import Cookie, User, Order, LineItem, Employee
from base import Base
from session import session


"""Inserting Data"""
print("\nInserting Data\n")

cc_cookie = Cookie(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity=12,
    unit_cost=0.50,
)

session.add(cc_cookie)
# Records are only inserted when commit is called
session.commit()
print(cc_cookie.cookie_id)


dcc = Cookie(
    cookie_name="dark chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe_dark.html",
    cookie_sku="CC02",
    quantity=1,
    unit_cost=0.75,
)
mol = Cookie(
    cookie_name="molasses",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe_molasses.html",
    cookie_sku="MOL01",
    quantity=1,
    unit_cost=0.80,
)

session.add(dcc)
session.add(mol)
# use flush if you expect additional work
# to be done on the objects after insertion
session.flush()
print(dcc.cookie_id)
print(mol.cookie_id)

c1 = Cookie(
    cookie_name="peanut butter",
    cookie_recipe_url="http://some.aweso.me/cookie/peanut.html",
    cookie_sku="PB01",
    quantity=24,
    unit_cost=0.25,
)
c2 = Cookie(
    cookie_name="oatmeal raisin",
    cookie_recipe_url="http://some.okay.me/cookie/raisin.html",
    cookie_sku="EWW01",
    quantity=100,
    unit_cost=1.00,
)

# c1 and c2 will not be
# associated with the session
session.bulk_save_objects([c1, c2])
session.commit()
print(c1.cookie_id)  # None
print(c2.cookie_id)  # None


"""Querying Data"""
print("\nQuerying Data\n")

# Select *
cookies = session.query(Cookie).all()
print(cookies)

# Iteration
for cookie in session.query(Cookie):
    print(cookie)

# Columns
print(session.query(Cookie.cookie_name, Cookie.quantity).first())

# Ordering
for cookie in session.query(Cookie).order_by(Cookie.quantity):
    print("{:3} - {}".format(cookie.quantity, cookie.cookie_name))

for cookie in session.query(Cookie).order_by(desc(Cookie.quantity)):
    print("{:3} - {}".format(cookie.quantity, cookie.cookie_name))

# Limiting
query = session.query(Cookie).order_by(Cookie.quantity)[:2]
print([result.cookie_name for result in query])

query = session.query(Cookie).order_by(Cookie.quantity).limit(2)
print([result.cookie_name for result in query])

# Functions and Labels
inv_count = session.query(func.sum(Cookie.quantity)).scalar()
print(inv_count)

rec_count = session.query(func.count(Cookie.cookie_name)).first()
print(rec_count)

rec_count = session.query(
    func.count(Cookie.cookie_name).label("inventory_count")
).first()
print(rec_count.keys())
print(rec_count.inventory_count)

# Filtering
record = session.query(Cookie).filter(Cookie.cookie_name == "chocolate chip").first()
print(record)

record = session.query(Cookie).filter_by(cookie_name="chocolate chip").first()
print(record)

query = session.query(Cookie).filter(Cookie.cookie_name.like("%chocolate%"))
for record in query:
    print(record.cookie_name)

# Operators
results = session.query(Cookie.cookie_name, "SKU-" + Cookie.cookie_sku).all()
for row in results:
    print(row)

query = session.query(
    Cookie.cookie_name,
    cast((Cookie.quantity * Cookie.unit_cost), Numeric(12, 2)).label("inv_cost"),
)
for result in query:
    print("{} - {}".format(result.cookie_name, result.inv_cost))

# Boolean operators / Conjunctions
query = session.query(Cookie).filter(Cookie.quantity > 23, Cookie.unit_cost < 0.40)
for result in query:
    print(result.cookie_name)

query = session.query(Cookie).filter(
    or_(Cookie.quantity.between(10, 50), Cookie.cookie_name.contains("chip"))
)
for result in query:
    print(result.cookie_name)

"""Updating Data"""
print("\nUpdating Data\n")

query = session.query(Cookie)
cc_cookie = query.filter(Cookie.cookie_name == "chocolate chip").first()
cc_cookie.quantity = cc_cookie.quantity + 120
session.commit()
print(cc_cookie.quantity)

# update in place (outside session)
query = session.query(Cookie)
query = query.filter(Cookie.cookie_name == "chocolate chip")
query.update({Cookie.quantity: Cookie.quantity - 20})

cc_cookie = query.first()
print(cc_cookie.quantity)

"""Deleting Data"""
print("\nDeleting Data\n")

query = session.query(Cookie)
query = query.filter(Cookie.cookie_name == "dark chocolate chip")
dcc_cookie = query.one()
session.delete(dcc_cookie)
session.commit()
dcc_cookie = query.first()
print(dcc_cookie)

# delete in place (outside session)
query = session.query(Cookie)
query = query.filter(Cookie.cookie_name == "molasses")
query.delete()
mol_cookie = query.first()
print(mol_cookie)

"""Load up some data"""
print("\nLoad up some data\n")

# Users
cookiemon = User(
    username="cookiemon",
    email_address="mon@cookie.com",
    phone="111-111-1111",
    password="password",
)
cakeeater = User(
    username="cakeeater",
    email_address="cakeeater@cake.com",
    phone="222-222-2222",
    password="password",
)
pieperson = User(
    username="pieperson",
    email_address="person@pie.com",
    phone="333-333-3333",
    password="password",
)
session.add(cookiemon)
session.add(cakeeater)
session.add(pieperson)
session.commit()

# Adding related objects - order 1
o1 = Order()
o1.user = cookiemon
session.add(o1)

cc = session.query(Cookie).filter(Cookie.cookie_name == "chocolate chip").one()
line1 = LineItem(cookie=cc, quantity=2, extended_cost=1.00)

pb = session.query(Cookie).filter(Cookie.cookie_name == "peanut butter").one()
line2 = LineItem(quantity=12, extended_cost=3.00)
line2.cookie = pb
line2.order = o1

o1.line_items.append(line1)
o1.line_items.append(line2)
session.commit()

# Adding related objects - order 2
o2 = Order()
o2.user = cakeeater

cc = session.query(Cookie).filter(Cookie.cookie_name == "chocolate chip").one()
line1 = LineItem(cookie=cc, quantity=24, extended_cost=12.00)

oat = session.query(Cookie).filter(Cookie.cookie_name == "oatmeal raisin").one()
line2 = LineItem(cookie=oat, quantity=6, extended_cost=6.00)

o2.line_items.append(line1)
o2.line_items.append(line2)

# SQLalchemy ensures the proper order to create the objects
session.add(o2)
session.commit()

"""Joins"""
print("\nJoins\n")

query = session.query(
    Order.order_id,
    User.username,
    User.phone,
    Cookie.cookie_name,
    LineItem.quantity,
    LineItem.extended_cost,
)
query = query.join(User).join(LineItem).join(Cookie)
results = query.filter(User.username == "cookiemon").all()
print(results)

# outer join
query = session.query(User.username, func.count(Order.order_id))
query = query.outerjoin(Order).group_by(User.username)
for row in query:
    print(row)

"""Self-referential table"""
print("\nSelf-referential table\n")


marsha = Employee(name="Marsha")
fred = Employee(name="Fred")
marsha.reports.append(fred)
session.add(marsha)
session.commit()

for report in marsha.reports:
    print(report.name)

"""Grouping"""
print("\nGrouping\n")

query = session.query(User.username, func.count(Order.order_id))
query = query.outerjoin(Order).group_by(User.username)
for row in query:
    print(row)

"""Chaining"""
print("\nChaining\n")


def get_orders_by_customer(cust_name, shipped=None, details=False):
    query = session.query(Order.order_id, User.username, User.phone)
    query = query.join(User)
    if details:
        query = query.add_columns(
            Cookie.cookie_name, LineItem.quantity, LineItem.extended_cost
        )
        query = query.join(LineItem).join(Cookie)
    if shipped is not None:
        query = query.filter(Order.shipped == shipped)
    results = query.filter(User.username == cust_name).all()
    return results


print(get_orders_by_customer("cakeeater"))
print(get_orders_by_customer("cakeeater", details=True))
print(get_orders_by_customer("cakeeater", shipped=True))
print(get_orders_by_customer("cakeeater", shipped=False))
print(get_orders_by_customer("cakeeater", shipped=False, details=True))

"""Raw Queries"""
print("\nRaw Queries\n")

query = session.query(User).filter(text("username='cookiemon'"))
print(query.all())
