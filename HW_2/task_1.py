from flask import Flask, redirect, render_template, request, make_response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('user_form.html')


@app.route('/login/', methods=['POST'])
def login():
    username = request.form.get('username')
    email = request.form.get('email')
    response = make_response(redirect('/welcome'))
    response.set_cookie('username', username)
    response.set_cookie('email', email)
    return response


@app.route('/welcome/')
def welcome():
    name = request.cookies.get('username')
    if name:
        return render_template('welcome.html', username=name)
    else:
        return redirect('/')


@app.route('/logout/', methods=['POST'])
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie('username')
    response.delete_cookie('email')
    return response


if __name__ == '__main__':
    app.run(debug=True)
