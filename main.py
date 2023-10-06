import math, sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, flash, redirect, session, abort



from data import queries

load_dotenv()
app = Flask('codecool_series')
SHOWS_PER_PAGE = 15
SHOWN_PAGE_NUMBERS = 5
app.secret_key = '!@34%^78'



@app.route('/')
def index():
    shows = queries.get_shows()
    return render_template('index.html', shows=shows)


@app.route('/design')
def design():
    return render_template('design.html')

@app.route('/actors')
def actors():
    actors=queries.get_actors()
    # print(actors)
    return render_template('actors.html', actors=actors)

# @app.route('/actors/<int:title>/')
# def actor_movie(title):
#     actors = queries.get_actors1(title)
#     return jsonify(actors)

@app.route('/actors/getShows', methods=['Post'])
def get_shows():
    id=request.form["id"]
    data=queries.get_actors_show(id)
    return jsonify({"data":data})

@app.route('/film/<string:name>')
def films(name):
    film_data = queries.films(name)
    # print(film_data)
    return render_template("film_detal.html", film_data=film_data)

@app.route('/allshows')
def all_shows():
    allfilm = queries.all_shows()
    return render_template("all_shows.html", allfilm=allfilm)



@app.route('/show/<int:id>/seasons')
def show_season(id):
    seasons = queries.get_seasons(id)
    return render_template('seasons_for_show.html', show=show, seasons=seasons)

# @app.route('/shows/')
@app.route('/shows/<int:page_number>')
@app.route('/shows/most-rated/')
@app.route('/shows/most-rated/<int:page_number>')
@app.route('/shows/order-by-<order_by>/')
@app.route('/shows/order-by-<order_by>-<order>/')
@app.route('/shows/order-by-<order_by>/<int:page_number>')
@app.route('/shows/order-by-<order_by>-<order>/<int:page_number>')
@app.route('/shows/')
def shows(page_number=1, order_by="rating", order="DESC"):
    count = queries.get_show_count()
    pages_count = math.ceil(count[0]['count'] / SHOWS_PER_PAGE)
    shows = queries.get_shows_limited(order_by, order, SHOWS_PER_PAGE, (page_number - 1) * SHOWS_PER_PAGE)

    shown_pages_start = int(page_number - ((SHOWN_PAGE_NUMBERS - 1) / 2))
    shown_pages_end = int(page_number + ((SHOWN_PAGE_NUMBERS - 1) / 2))
    if shown_pages_start < 1:
        shown_pages_start = 1
        shown_pages_end = SHOWN_PAGE_NUMBERS
    elif shown_pages_end > pages_count:
        shown_pages_start = pages_count - SHOWN_PAGE_NUMBERS + 1
        shown_pages_end = pages_count

    return render_template(
        'shows.html',
        shows=shows,
        pages_count=pages_count,
        page_number=page_number,
        shown_pages_start=shown_pages_start,
        shown_pages_end=shown_pages_end,
        order_by=order_by,
        order=order
    )


@app.route('/show/<int:id>/')
def show(id):
    show = queries.get_show(id)
    characters = queries.get_show_characters(id, 3)
    seasons = queries.get_show_seasons(id)

    # format character names
    show['characters_str'] = \
        ', '.join([character['name'] for character in characters])

    # getting trailer id from URL to embed video
    show['trailer_id'] = \
        show['trailer'][show['trailer'].find('=')+1:] if show['trailer'] else ''

    # format runtime
    hours, minutes = divmod(show['runtime'], 60)
    runtime_str = (str(hours)+'h ' if hours else '') + (str(minutes)+'min' if minutes else '')
    show['runtime_str'] = runtime_str

    return render_template('show.html', show=show, seasons=seasons)


@app.route('/episode/<int:id>/')
def get_episode(id):
    episode = queries.get_episode(id)

    return render_template('episode.html', episode=episode)

@app.route('/api/actors/<int:show_id>/')
def get_actors(show_id):
    data = queries.get_actors1(show_id)

    return jsonify(data)




@app.route('/save-rating', methods=['POST'])
def save_rating():
    try:
        # Odbieranie danych z formularza
        rating = request.json['rating']

        # Zapisanie oceny w bazie danych
        conn = sqlite3.connect('egzamin.db')
        c = conn.cursor()
        c.execute('INSERT INTO ratings (value) VALUES (?)', (rating,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except:
        return jsonify({'success': False})


@app.route('/actor/<int:id>', methods=["GET"])
def actor(id):
    data=queries.get_actor(id)
    if len(data)==0:
        abort(404)
    return render_template("actor_details.html", actor=data[0])

@app.route('/api/actor/<int:id>', methods=["GET"])
def actor1(id):
    data=queries.get_actor(id)
    if len(data)==0:
        abort(404)
    return jsonify(data)


@app.route('/actor/genres', methods=["POST"])
def genres():
    id = request.form["id"]
    data = queries.get_actor_genres(id)
    return_data=[]
    for genres in data:
        if genres["name"] not in return_data:
            return_data.append(genres["name"])
    return jsonify({"data": return_data})


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
