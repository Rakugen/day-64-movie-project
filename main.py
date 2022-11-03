from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, URL, NumberRange
import requests
import config

app = Flask(__name__)
app.app_context().push()
API_KEY = config.api_key
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


# TABLES:
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, unique=True, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'


# FORMS:
class AddForm(FlaskForm):
    title = StringField('Title:', validators=[DataRequired()])
    year = IntegerField('Year:', validators=[DataRequired()])
    description = StringField('Description:', validators=[DataRequired()])
    rating = FloatField('Rating:', validators=[DataRequired(), NumberRange(min=0, max=10)])
    ranking = IntegerField('Rank:', validators=[DataRequired()])
    review = StringField('Review:', validators=[DataRequired()])
    img_url = StringField('IMG URL:', validators=[DataRequired(), URL()])
    submit = SubmitField('Add Movie')


class EditForm(FlaskForm):
    rating = FloatField('Your Rating Out of 10 (ex. 7.5):', validators=[DataRequired(), NumberRange(min=0, max=10)])
    review = StringField('Your Review:', validators=[DataRequired()])
    submit = SubmitField('Update')


db.create_all()


# ROUTES:
@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_movie = Movie(
            title=form.title.data,
            year=form.year.data,
            description=form.description.data,
            rating=form.rating.data,
            ranking=form.ranking.data,
            review=form.review.data,
            img_url=form.img_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


@app.route("/edit/<movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    movie = Movie.query.get(movie_id)
    form = EditForm()
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/select")
def select():
    return render_template("select.html")


@app.route("/delete/<movie_id>", methods=["GET"])
def delete(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
