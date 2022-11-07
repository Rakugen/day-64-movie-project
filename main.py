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
API_ENDPOINT = "https://api.themoviedb.org/3/"
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
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
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
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    # for index, movie in enumerate(all_movies):
    #     movie.ranking = len(all_movies) - index

    db.session.commit()
    all_movies = Movie.query.order_by(Movie.ranking).all()

    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        parameters = {
            "api_key": API_KEY,
            "query": movie_title
        }
        response = requests.get(f"{API_ENDPOINT}/search/movie", params=parameters)
        response.raise_for_status()
        data = response.json()["results"]
        return render_template("select.html", data=data)
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


@app.route("/movie_search/<int:movie_id>")
def movie_search(movie_id):
    parameters = {
        "api_key": API_KEY,
        "movie_id": movie_id
    }
    movie_search_url = f"{API_ENDPOINT}/movie/{movie_id}"
    response = requests.get(movie_search_url, params=parameters)
    response.raise_for_status()
    data = response.json()
    new_movie = Movie(
        title=data["original_title"],
        img_url="https://image.tmdb.org/t/p/w300_and_h450_bestv2"+data["poster_path"],
        year=data["release_date"],
        description=data["overview"]
    )
    db.session.add(new_movie)
    db.session.commit()
    db.session.flush()
    return redirect(url_for('edit', movie_id=new_movie.id))


@app.route("/delete/<movie_id>", methods=["GET"])
def delete(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
