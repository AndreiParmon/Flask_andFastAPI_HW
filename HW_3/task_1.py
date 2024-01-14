from flask import Flask, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect

from HW_3.forms import RegistrationForm
from HW_3.models import db, User

from hashlib import sha256

app = Flask(__name__)
app.config['SECRET_KEY'] = b'c9285a38f72aec0fa95bbfeb547211f0aa808ec18649658d3e7279c47e1e4042'
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../instance/database.db'

db.init_app(app)


@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('OK')


@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Обработка данных из форм
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=sha256(form.password.data.encode(encoding='utf-8')).hexdigest())
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('register'))
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
