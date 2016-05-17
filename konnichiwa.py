from flask import Flask, jsonify, make_response, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi
import cgitb
import json
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.fields import TextAreaField
from flask_mail import Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask.ext.security.utils import encrypt_password
from flask_security.core import current_user, AnonymousUser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messageboard.db'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'CS330Final@gmail.com'
app.config['MAIL_PASSWORD'] = 'Robiechan'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'hi'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_REGISTER_URL'] = '/create_account'

app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSOPO'

db = SQLAlchemy(app)
app.debug = True

mail = Mail()
mail.init_app(app)

Bootstrap(app)

roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')), db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

class Board(db.Model):
  __tablename__ = 'boards'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String) #title of board
  route = db.Column(db.String) #short title (route to page)
  numthreads = db.Column(db.Integer) #number of threads
  datemod = db.Column(db.DateTime) #date modified

class Thread(db.Model):
  __tablename__ = 'threads'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String) #title of thread
  board = db.Column(db.Integer) #board id
  numposts = db.Column(db.Integer) #number of posts
  datemod = db.Column(db.DateTime) #date modified

class Post(db.Model):
  __tablename__ = 'posts'
  id = db.Column(db.Integer, primary_key=True)
  user = db.Column(db.Integer) #user id
  thread = db.Column(db.Integer) #thread id
  title = db.Column(db.String) #post title
  message = db.Column(db.String) #post message
  datemod = db.Column(db.DateTime) #date modified

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    numposts = db.Column(db.Integer) #number of posts

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app = app, datastore=user_datastore)

#@app.before_first_request
#def create_user():
#  db.create_all()
#  user_datastore.create_user(email='test@test.fr', password=encrypt_password('password'))
#  db.session.commit()

db.create_all()

@app.route('/testuser')
@login_required
def testuser():
  return current_user.email.split('@')[0]

@app.route('/')
def konnichiwa():
  return redirect(url_for('listboards'))

@app.route('/boards')
def listboards():
  boards = Board.query.order_by(db.desc(Board.datemod)).all()
  threads = Thread.query.all()
  return render_template('boards.html', boards=boards)

class ThreadForm(Form):
  title = TextField("Title")
  message = TextAreaField("Message")

@app.route('/boards/<boardroute>', methods=["GET"])
def showboard(boardroute):
  form = ThreadForm(request.form, csrf_enabled=False)
  board = Board.query.filter_by(route=boardroute).first()
  threads = Thread.query.filter_by(board=board.id).order_by(db.desc(Thread.datemod)).all()
  return render_template('board.html',board=board, threads=threads, form=form)

class PostForm(Form):
  title = TextField("title")
  message = TextAreaField("message")

@app.route('/threads/<int:threadid>', methods=['GET'])
def showthread(threadid):
  form = PostForm(request.form, csrf_enabled=False)
  thread = Thread.query.filter_by(id=threadid).first()
  board = Board.query.filter_by(id=thread.board).first()
  posts = Post.query.filter_by(thread=threadid).order_by(db.desc(Post.datemod)).all()
  return render_template('thread.html', board=board, thread=thread, posts=posts, form = form)

#api
@app.route('/api')
def apiref():
  return render_template('apiref.html')

@app.route('/api/add/board', methods=['POST'])
def api_add_board():
  resp = make_response()
  outobj = {}
  resp.headers["Content-type"] = "application/json"
  data = json.loads(request.data.decode('utf8'))
  checkTitle = Board.query.filter_by(title=data["title"]).first()
  checkRoute = Board.query.filter_by(route=data["route"]).first()
  if data["title"] == None or str(data["title"]).strip() == "":
    outobj["error"] = "Title must not be empty"
  elif not (checkTitle == None or checkRoute == None):
    outobj["error"] = "board already exists"
  else:
    board = Board(title=data["title"], route=data["route"], numthreads=0, datemod=datetime.now())
    db.session.add(board)
    db.session.commit()
  out = json.dumps(outobj)
  resp.set_data(out)
  return resp

@app.route('/api/add/thread', methods=['POST'])
def api_add_thread():
  resp = make_response()
  outobj = {}
  resp.headers["Content-type"] = "application/json"
  data = json.loads(request.data.decode('utf8'))
  board = Board.query.filter_by(id=data["board"]).first()
  if data["board"] == None:
    outobj["error"] = "Invalid Board ID"
  elif data["title"] == None or str(data["title"]).strip() == "":
    outobj["error"] = "Title must not be empty"
  elif data["message"] == None or str(data["message"]).strip() == "":
    outobj["error"] = "Message mut not be empty"
  else:
    board.numthreads += 1
    board.datemod = datetime.now()
    thread = Thread(title=data["title"], board=data["board"], numposts=1, datemod=datetime.now())
    db.session.add(thread)
    db.session.commit()
    try:
      post = Post(title=data["title"],thread=thread.id,user=current_user.email.split('@')[0], message=data["message"], datemod=datetime.now())
      outobj["username"] = current_user.email.split('@')[0]
    except:
      post = Post(title=data["title"],thread=thread.id,user="Anonymous", message=data["message"], datemod=datetime.now())
      outobj["username"] = "Anonymous"
    db.session.add(post)
    db.session.commit()
    outobj["thread"] = thread.id
  out = json.dumps(outobj)
  resp.set_data(out)
  return resp

@app.route('/api/add/post', methods=['POST'])
def api_add_post():
  resp = make_response()
  outobj = {}
  resp.headers["Content-type"] = "application/json"
  data = json.loads(request.data.decode('utf8'))
  thread = Thread.query.filter_by(id=data["thread"]).first()
  board = Board.query.filter_by(id=thread.board).first()
  if thread == None:
    outobj["error"] = "Invalid thread ID"
  elif data["title"] == None or str(data["title"]).strip() == "":
    outobj["error"] = "Title must not be empty"
  elif data["message"] == None or str(data["message"]).strip() == "":
    outobj["error"] = "Message must not be empty"
  else:
    thread.numposts += 1
    thread.datemod = datetime.now()
    board.datemod = datetime.now()
    try:
      post = Post(title=data["title"],thread=thread.id,user=current_user.email.split('@')[0], message=data["message"], datemod = datetime.now())
      outobj["username"] = current_user.email.split('@')[0]
    except:
      post = Post(title=data["title"],thread=thread.id,user="Anonymous", message=data["message"], datemod = datetime.now())
      outobj["username"] = "Anonymous"
    db.session.add(post)
    db.session.commit()
  out = json.dumps(outobj)
  resp.set_data(out)
  return resp

@app.route('/api/get/boardid')
def api_get_board_id():
  data = json.loads(request.data.decode('utf8'))
  board = Board.query.filter_by().first()
  outobj = {"boardid" : board.id}
  resp = make_response(json.dumps(outobj))
  return resp

@app.route('/api/get/boards')
def api_get_boards():
  boards = Board.query.order_by(db.desc(Board.datemod)).all()
  outobj = []
  for board in boards:
    outobj.append({"title" : board.title, "route" : board.route, "numthreads" : board.numthreads, "datemod" : board.datemod.isoformat()})
  resp = make_response(json.dumps(outobj))
  return resp

@app.route('/api/get/threads')
def api_get_threads():
  data = json.loads(request.data.decode('utf8'))
  outobj = []
  threads = Thread.query.filter_by(board = data["board"]).order_by(db.desc(Thread.datemod)).all()
  for thread in threads:
    outobj.append({"id" : thread.id, "title" : thread.title, "board" : thread.board, "numposts" : thread.numposts, "datemod" : thread.datemod.isoformat()})
  resp = make_response(json.dumps(outobj))
  return resp

@app.route('/api/get/posts')
def api_get_posts():
  data = json.loads(request.data.decode('utf8'))
  outobj = []
  posts = Post.query.filter_by(thread = data["thread"]).order_by(db.desc(Post.datemod)).all()
  for post in posts:
    outobj.append({"id" : post.id, "user" : post.user, "thread" : post.thread, "title" : post.title, "message" : post.message, "datemod" : post.datemod.isoformat()})
  resp = make_response(json.dumps(outobj))
  return resp

if __name__ == '__main__':
  app.run()
