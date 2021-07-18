from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import SubmitField, StringField, HiddenField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL
from werkzeug.security import generate_password_hash, check_password_hash
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI1', 'sqlite:///cafes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class ListCafes(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    wifi = db.Column(db.String(250), nullable=False)
    coffee = db.Column(db.String(250), nullable=False)
    power = db.Column(db.String(250), nullable=False)
    open_time = db.Column(db.String(250), nullable=False)
    closing_time = db.Column(db.String(250), nullable=False)
    website = db.Column(db.String(250), nullable=False)
    image1 = db.Column(db.String(250), nullable=False)
    image2 = db.Column(db.String(250), nullable=False)
    image3 = db.Column(db.String(250), nullable=False)
    count_rate = db.Column(db.String(250), nullable=False)
    secret_key = db.Column(db.String(250), nullable=False)


db.create_all()


class AddForm(FlaskForm):
    some_hidden_field = HiddenField()
    name = StringField('Cafe Name', validators=[DataRequired()])
    description = StringField('Description of the Cafe', validators=[DataRequired()])
    address = StringField('Cafe Address', validators=[DataRequired()])
    open = StringField('Cafe Opening Time (10am or 6pm)', validators=[DataRequired()])
    close = StringField('Cafe Closing Time (10am or 6pm)', validators=[DataRequired()])
    website = StringField('Link to the Cafe Website', validators=[DataRequired(), URL()])
    image1 = StringField('First Image for Image Carousel', validators=[DataRequired(), URL()])
    image2 = StringField('Second Image for Image Carousel', validators=[DataRequired(), URL()])
    image3 = StringField('Third Image for Image Carousel', validators=[DataRequired(), URL()])
    secret_key = StringField('Key for Changing Аnd Deleting Cafes', validators=[DataRequired()])
    submit = SubmitField('OK')


class UpdateForm(FlaskForm):
    some_hidden_field = HiddenField()
    name = StringField('Cafe Name', validators=[DataRequired()])
    description = StringField('Description of the Cafe', validators=[DataRequired()])
    address = StringField('Cafe Address', validators=[DataRequired()])
    open = StringField('Cafe Opening Time (10am or 6.05pm)', validators=[DataRequired()])
    close = StringField('Cafe Closing Time (10am or 6.05pm)', validators=[DataRequired()])
    website = StringField('Link to the Cafe Website', validators=[DataRequired(), URL()])
    image1 = StringField('First Image for Image Carousel', validators=[DataRequired(), URL()])
    image2 = StringField('Second Image for Image Carousel', validators=[DataRequired(), URL()])
    image3 = StringField('Third Image for Image Carousel', validators=[DataRequired(), URL()])
    submit = SubmitField('OK')


class CheckKey(FlaskForm):
    some_hidden_field = HiddenField()
    key = StringField('Enter the Key')
    submit = SubmitField('OK')


@app.route('/')
def home():
    all_cafes = ListCafes.query.all()
    return render_template('index.html', cafes=all_cafes)


@app.route('/<cafe_name>', methods=['POST', 'GET'])
def cafe(cafe_name):
    that_cafe = ListCafes.query.filter_by(name=cafe_name).first()
    if request.method == 'POST':
        that_cafe.coffee = str(int(that_cafe.coffee) + int(request.form['coffee']))
        that_cafe.wifi = str(int(that_cafe.wifi) + int(request.form['wifi_power']))
        that_cafe.power = str(int(that_cafe.power) + int(request.form['power_socket']))
        that_cafe.count_rate = str(int(that_cafe.count_rate) + 5)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('cafe.html', cafe=that_cafe, cafe_name1=cafe_name)


@app.route('/<cafe_id>/<do>/check_key', methods=['GET', 'POST'])
def check_key(do, cafe_id):
    form = CheckKey()
    that_cafe = ListCafes.query.get(cafe_id)
    if form.validate_on_submit():
        if not check_password_hash(that_cafe.secret_key, form.key.data):
            flash('You Entered the Wrong Key!')
        elif do == 'delete' and check_password_hash(that_cafe.secret_key, form.key.data):
            return redirect(url_for('delete', cafe_name=that_cafe.name))
        elif do == 'update' and check_password_hash(that_cafe.secret_key, form.key.data):
            return redirect(url_for('update', cafe_name=that_cafe.name))

    return render_template('check.html', do1=do, form=form, cafe_id1=cafe_id)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        hash_and_salted_key = generate_password_hash(form.secret_key.data, method='pbkdf2:sha256', salt_length=8)
        new_cafe = ListCafes(name=form.name.data, description=form.description.data, address=form.address.data,
                             wifi='0',
                             coffee='0', power='0', open_time=form.open.data, closing_time=form.close.data,
                             website=form.website.data, image1=form.image1.data, image2=form.image2.data,
                             image3=form.image3.data, count_rate='0', secret_key=hash_and_salted_key)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


@app.route('/<cafe_name>/update', methods=['POST', 'GET'])
def update(cafe_name):
    that_cafe = ListCafes.query.filter_by(name=cafe_name).first()
    form = UpdateForm(name=that_cafe.name, description=that_cafe.description, address=that_cafe.address,
                      open=that_cafe.open_time, close=that_cafe.closing_time, website=that_cafe.website,
                      image1=that_cafe.image1, image2=that_cafe.image2, image3=that_cafe.image3)
    if form.validate_on_submit():
        that_cafe.name = form.name.data
        that_cafe.description = form.description.data
        that_cafe.address = form.address.data
        that_cafe.open_time = form.open.data
        that_cafe.closing_time = form.close.data
        that_cafe.website = form.website.data
        that_cafe.image1 = form.image1.data
        that_cafe.image2 = form.image2.data
        that_cafe.image3 = form.image3.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update.html', cafe_name1=cafe_name, form=form)


@app.route('/<cafe_name>/delete', methods=['GET', 'POST'])
def delete(cafe_name):
    that_cafe = ListCafes.query.filter_by(name=cafe_name).first()
    db.session.delete(that_cafe)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
