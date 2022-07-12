from flask import render_template,redirect,session,request, flash
from flask_app import app
from flask_app.models import user
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask import flash

@app.route('/main')
def index():
    return render_template('main.html')

@app.route('/register',methods=['POST'])
def register():
    if not user.User.validate_register(request.form):
        return redirect('/main')
    data = {
        "name" : request.form['name'],
        "alias": request.form['alias'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password'])
    }
    id = user.User.save(data)
    session['user_id'] = id
    return redirect('/pokes')

@app.route('/login',methods=['POST'])
def login():
    valid_user = user.User.get_email(request.form)
    if not valid_user:
        flash("Invalid Email","login")
        return redirect('/main')
    userpword= bcrypt.check_password_hash(valid_user.password, request.form['password'])
    print(userpword)
    if not userpword:
        flash("Invalid Password","login")
        return redirect('/main')
    session['user_id'] = valid_user.id
    return redirect('/pokes')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/main')



@app.route('/pokes')
def pokes_dash():
    if 'user_id' not in session:
        return redirect('/main')
    data ={
        'id': session['user_id']
    }
    valid_user = user.User.get_ONE_user_with_pokes(data)
    poke_list = user.User.get_all_pokers()
    return render_template("pokes.html", user = valid_user, poke_list = poke_list)

@app.route('/poke_them/<int:id>')
def poke_them(id):
    if 'user_id' not in session:
        return redirect('/main')
    data= {
        'user_id': id,
        'poker_id': session['user_id'],
        }
    if not user.User.check_pokes(data):
        user.User.start_pokin(data)
        print("started to poke!")
        return redirect('/pokes')

    else:
        user.User.add_poke(data)
        print("poked again!")
        return redirect('/pokes')


    