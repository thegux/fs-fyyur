#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ARRAY, String, Integer, ForeignKey, Numeric, Boolean
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model):
    __tablename__ = 'Shows'
    id = Column(Integer, primary_key=True)
    venue_id = Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = Column(db.DateTime, default=datetime.utcnow())


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    address = Column(String(120))
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    genres = db.Column(db.ARRAY(db.String), nullable = False)
    website = Column(String(500))
    seeking_talent = Column(Boolean(), default=False)
    seeking_description = Column(String(1000))
    shows = db.relationship('Shows', backref='Venue', lazy=True)



class Artist(db.Model):
    __tablename__ = 'Artist'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    genres = db.Column(db.ARRAY(db.String), nullable = False)
    image_link = Column(String(2000))
    facebook_link = Column(String(120))
    website = Column(String(500))
    seeking_venue = Column(Boolean(), default=False)
    seeking_description = Column(String(1000))
    shows = db.relationship('Shows', backref='Artist', lazy=True)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_venues = Venue.query.all()
    aux_venues = []
    for venue in all_venues:
        venues_by_areas = Venue.query.filter_by(
            state=venue.state).filter_by(city=venue.city)
        venue_details = []
        for ven in venues_by_areas:
            venue_details.append({
                'id': ven.id,
                'name': ven.name,
                'num_upcoming_shows': len(Shows.query.filter(Shows.venue_id == ven.id).filter(Shows.start_time > datetime.utcnow()).all()) if len(Shows.query.all()) > 0 else 0
            })
        aux_venues.append(
            {'city': venue.city, 'state': venue.state, "venues": venue_details})
    return render_template('pages/venues.html', areas=aux_venues)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '').lower()
    all_venues = Venue.query.all()
    filtered = []
    for venue in all_venues:
        if search_term in venue.name.lower():
            filtered.append(venue)

    data = []
    for ven in filtered:
        data.append({
            'id': ven.id,
            'name': ven.name,
            'num_upcoming_shows': len(db.session.query(Shows).filter(Shows.venue_id == ven.id).filter(Shows.start_time > datetime.utcnow()).all()) if len(db.session.query(Shows).all()) > 0 else 0
        })

    response = {
        "count": len(filtered),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    if(not venue):
        flash("There is no Venue with id {}.".format(venue_id))
        return render_template('pages/home.html')

    venue_shows = Shows.query.filter_by(venue_id=venue_id)
    new_shows = venue_shows.filter(Shows.start_time > datetime.utcnow()).all()
    aux_future_shows = []
    for show in new_shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        aux_future_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })


    old_shows = venue_shows.filter(Shows.start_time < datetime.utcnow()).all()
    aux_past_shows = []
    for show in old_shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        aux_past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    data = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent if venue.seeking_talent else False,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": aux_past_shows,
        "upcoming_shows": aux_future_shows,
        "past_shows_count": len(aux_past_shows),
        "upcoming_shows_count": len(aux_future_shows),
    }
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    body = {}
    try:
        form = VenueForm()
        new_venue = Venue(
            name=form.name.data,
            genres=form.genres.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if(error):
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        abort(400)
    else:
        flash('The Venue was successfully created')
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    all_artists = Artist.query.all()
    artist_data = []
    for item in all_artists:
        artist_data.append({
            "id": item.id,
            'name': item.name,
        })
    return render_template('pages/artists.html', artists=artist_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '').lower()
    all_artists = Artist.query.all()
    filtered = []
    for artist in all_artists:
        if search_term in artist.name.lower():
            filtered.append(artist)

    data = []
    for art in filtered:
        data.append({
            'id': art.id,
            'name': art.name,
            'num_upcoming_shows': len(db.session.query(Shows).filter(Shows.artist_id == art.id).filter(Shows.start_time > datetime.utcnow()).all()) if len(db.session.query(Shows).all()) > 0 else 0
        })

    response = {
        "count": len(filtered),
        "data": data
    }
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    if(not artist):
        flash("There is no Artist with id {}.".format(artist_id))
        return render_template('pages/home.html')

    artist_shows = Shows.query.filter_by(artist_id=artist_id)
    new_shows = artist_shows.filter(Shows.start_time > datetime.utcnow()).all()
    aux_future_shows = []
    for show in new_shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        aux_future_shows.append({
            "venue_id": show.artist_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })


    old_shows = artist_shows.filter(Shows.start_time < datetime.utcnow()).all()
    aux_past_shows = []
    for show in old_shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        aux_past_shows.append({
            "venue_id": show.artist_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue if artist.seeking_venue else False,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": aux_past_shows,
        "upcoming_shows": aux_future_shows,
        "past_shows_count": len(aux_past_shows),
        "upcoming_shows_count": len(aux_future_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    aux_artist = Artist.query.filter_by(id=artist_id).first()
    form.name.data = aux_artist.name
    form.genres.data = aux_artist.genres
    form.city.data =  aux_artist.city
    form.state.data = aux_artist.state
    form.phone.data = aux_artist.phone
    form.facebook_link.data = aux_artist.facebook_link

    artist = {
        "id": artist_id,
        "name": aux_artist.name,
        "genres": aux_artist.genres,
        "city": aux_artist.city,
        "state": aux_artist.state,
        "phone": aux_artist.phone,
        "website": aux_artist.website,
        "facebook_link": aux_artist.facebook_link,
        "seeking_venue": aux_artist.seeking_venue if aux_artist.seeking_venue else False,
        "seeking_description": aux_artist.seeking_description,
        "image_link": aux_artist.image_link
    }
    
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        db.session.commit()
    except:
        print(sys.exc_info())
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if(error):
        flash('An error occurred while updating the artist.')
        return render_template('pages/home.html')
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))





@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    aux_venue = Venue.query.get(venue_id)
    form.name.data = aux_venue.name
    form.genres.data = aux_venue.genres
    form.address.data = aux_venue.address
    form.city.data = aux_venue.city
    form.state.data = aux_venue.state
    form.phone.data = aux_venue.phone
    form.facebook_link.data = aux_venue.facebook_link

    venue = {
        "id": venue_id,
        "name": aux_venue.name,
        "genres": aux_venue.genres,
        "address": aux_venue.address,
        "city": aux_venue.city,
        "state": aux_venue.state,
        "phone": aux_venue.phone,
        "website": aux_venue.website,
        "facebook_link": aux_venue.facebook_link,
        "seeking_talent": aux_venue.seeking_talent if aux_venue.seeking_talent else True,
        "seeking_description": aux_venue.seeking_description,
        "image_link": aux_venue.image_link,
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        db.session.commit()
    except:
        print(sys.exc_info())
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if(error):
        flash('An error occurred while updating the venue.')
        return render_template('pages/home.html')
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))






#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    try:
        form = ArtistForm()
        new_artist =    Artist(
            name =  form.name.data,
            city = form.city.data,
            state = form.state.data,
            phone = form.phone.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data
        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if(error):
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        abort(400)
    else:
        flash('The Artist was successfully created')
        return render_template('pages/home.html')






#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    show_data = Shows.query.all()
    data = []
    for item in show_data:
        specific_venue = Venue.query.filter_by(id = item.venue_id).first()
        specific_artist = Artist.query.filter_by(id = item.artist_id).first()
        data.append({
            'venue_id': item.venue_id,
            'venue_name': specific_venue.name,
            'artist_id': item.artist_id,
            'artist_name': specific_artist.name,
            'artist_image_link': specific_artist.image_link,
            'start_time': item.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try: 
        form = ShowForm()
        new_show = Shows(
            venue_id = form.venue_id.data,
            artist_id = form.artist_id.data,
            start_time = form.start_time.data,
        )
        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if(error):
        flash('An error occurred. Show could not be listed.')
        abort(400)
    else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug = True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
