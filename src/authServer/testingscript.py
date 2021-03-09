import time
from app import app, db
from app.models import User, AuthToken, RefreshToken

u1 = User(username='maxim', password='foo', access_list=['kill','drive'])
u2 = User(username='iris',password='bar',access_list=['kill'])
u3 = User(username='cameron', password='baz', access_list=['carry', 'print money'])
db.session.add_all([u1,u2,u3])
db.session.commit()

user_id1 = u1.id

del u1
del u2
del u3

u1 = User.query.get(user_id1)
u3 = User.query.filter_by(username='cameron').first()
a1 = AuthToken(user=u1, access_list=['kill'], password='foo')
a2 = AuthToken(user=u3, access_list=['carry'], password='baz')
a3 = AuthToken(user=u3, access_list=['carry', 'print money'], password='baz')
db.session.add_all([a1, a2])
db.session.commit()
time.sleep(1)
db.session.add(a3)
db.session.commit()


print(AuthToken.query.all())
AuthToken.purge_expired()
print(AuthToken.query.all())
time.sleep(1)
AuthToken.purge_expired()
print(AuthToken.query.all())




u1 = User.query.get(1)
r1 = RefreshToken(u1, access_list=['drive'])
db.session.add(r1)
db.session.commit()

u3.delete()

r = RefreshToken.query.all()
a = AuthToken(User.query.get(r[0].user_id), refresh_token=r[0])
db.session.add(a)
db.session.commit()
print(a.expiration_date)
