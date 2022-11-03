import os
import requests
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange

app = Flask(__name__)
app.app_context().push()
API_KEY = os.environ['API_KEY']
API_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
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
    submit = SubmitField('Search Movies')


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
        # new_movie = Movie(
        #     title=form.title.data,
        # )
        # db.session.add(new_movie)
        # db.session.commit()
        return redirect(url_for('select', title=form.title.data))
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


@app.route("/select/<title>")
def select(title):
    # TODO: With title, search API and display the results in select.html
    #  Within select.html, have working links that uses the ID of the movie
    #  when clicked and will hit up another path in TMDB API, that will fetch
    #  all data on that specific movie(title, img_url, year, description).
    #  Once the entry is added, redirect to home
    parameters = {
        "api_key": API_KEY,
        "query": title
    }

    response = requests.get(API_ENDPOINT, params=parameters)
    response.raise_for_status()
    data = response.json()
    print(data)

    return render_template("select.html", movies=data["results"])


@app.route("/delete/<movie_id>", methods=["GET"])
def delete(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
