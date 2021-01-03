#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from forms import *
import sys
import config
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# app.config['SQLQLCHEMY_TRACK_MODIFICATIONS'] = False

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #PS
    website_link = db.Column(db.String(255))
    seeking_talent = db.Column(db.Boolean)
    seeking_talent_text = db.Column(db.String(255))
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # PS
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(255))
    #PS
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_venue_text = db.Column(db.String(255))
    shows = db.relationship('Show', backref='artist', lazy=True)
   
    # PS
    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}>'
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#PS
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  #PS
  data=[]
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for city in cities:
      venues_in_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
      data.append({
        "city": city[0],
        "state": city[1],
        "venues": venues_in_city
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  #PS
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in venues:
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(Show.venue_id == venue.id)
      for show in shows:
          if (show.start_time > datetime.now()):
              num_upcoming_shows += 1

      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })

  response={
        "count": len(venues),
        "data": data
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #PS
  venue = Venue.query.get(venue_id)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_talent_text": venue.seeking_talent_text,
    "image_link": venue.image_link
  }

  past_shows = db.session.query(Show).join(Venue).filter(Venue.id==venue.id, Show.start_time < datetime.now()).all()
  past_shows_list = []
  for show in past_shows:
    artist = Artist.query.get(show.artist_id)
    dict1 = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    past_shows_list.append(dict1)

  upcoming_shows = db.session.query(Show).join(Venue).filter(Venue.id==venue.id, Show.start_time > datetime.now()).all()
  upcoming_shows_list = []
  for show in upcoming_shows:
    artist = Artist.query.get(show.artist_id)
    dict1 = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    upcoming_shows_list.append(dict1)
  
  data["past_shows"] = past_shows_list
  data["upcoming_shows"] = upcoming_shows_list
  data["past_shows_count"] = len(past_shows_list)
  data["upcoming_shows_count"] = len(upcoming_shows_list)
  return render_template('pages/show_venue.html', venue=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  form.state.data = artist.state
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_venue_text.data = artist.seeking_venue_text
  form.genres.data = artist.genres
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website']
    artist.seeking_venue_text = request.form['seeking_venue_text']
    if 'seeking_venue' not in request.form:
      artist.seeking_venue = False
    else:
      artist.seeking_venue = True
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  #PS
    form = VenueForm(request.form)
    error = False
    try:
      venue = Venue(
          name = request.form['name'],
          genres = request.form.getlist('genres'),
          address = request.form['address'],
          city = request.form['city'],
          state = request.form['state'],
          phone = request.form['phone'],
          website_link = request.form['website_link'],
          facebook_link = request.form['facebook_link'],
          image_link = request.form['image_link'],
          #seeking_talent = request.form['seeking_talent'],
          seeking_talent_text = request.form['seeking_talent_text']
      )
      if 'seeking_talent' not in request.form:
        venue.seeking_talent = False
      else:
        venue.seeking_talent = True
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed!')
    finally:
      db.session.close()
      return render_template('pages/home.html')
   

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  #PS
  print("Venue delete function: ", venue_id)
  error = False
  name = ''
  try:
    venue = Venue.query.get(venue_id)
    db.session.query(Show).filter(Show.venue_id==venue_id).delete()
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
  else:
    flash('Venue ' + name+ ' deleted successfully')
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({"id":artist.id, "name" : artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  #PS
  search = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
  data = []
  for artist in artists:
    upcoming_shows = db.session.query(Show).join(Artist).filter(Artist.id==artist.id, Show.start_time > datetime.now()).count()
    print(upcoming_shows)
    data.append({
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows" : upcoming_shows
    })
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #PS
  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_venue_text": artist.seeking_venue_text,
    "image_link": artist.image_link
  }
  past_shows = db.session.query(Show).join(Artist).filter(Artist.id==artist.id, Show.start_time < datetime.now()).all()
  past_shows_list = []
  for show in past_shows:
    venue = Venue.query.get(show.venue_id)
    dict1 = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    past_shows_list.append(dict1)

  upcoming_shows = db.session.query(Show).join(Artist).filter(Artist.id==artist.id, Show.start_time > datetime.now()).all()
  upcoming_shows_list = []
  for show in upcoming_shows:
    venue = Venue.query.get(show.venue_id)
    dict1 = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    upcoming_shows_list.append(dict1)
  
  data["past_shows"] = past_shows_list
  data["upcoming_shows"] = upcoming_shows_list
  data["past_shows_count"] = len(past_shows_list)
  data["upcoming_shows_count"] = len(upcoming_shows_list)
  return render_template('pages/show_artist.html', artist=data)

#PS Artist Delete

@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
  error = False
  name = ''
  try:
    artist = Artist.query.get(artist_id)
    db.session.query(Show).filter(Show.artist_id==artist_id).delete()
    name = artist.name
    db.session.delete(artist)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + name + ' could not be deleted.')
  else:
    flash('Artist ' + name+ ' deleted successfully')
  return redirect(url_for('index'))

  # TODO: populate form with values from venue with ID <venue_id>

#PS
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  form.state.data = venue.state
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_talent_text.data = venue.seeking_talent_text
  form.genres.data = venue.genres
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  #PS
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form.getlist('genres')
    venue.website_link = request.form['website']
    venue.seeking_talent_text = request.form['seeking_talent_text']
    if 'seeking_talent' not in request.form:
      venue.seeking_talent = False
    else:
      venue.seeking_talent = True
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

#PS
  error = False
  try:
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      genres = request.form.getlist('genres'),
      website_link = request.form['website_link'],
      seeking_venue_text = request.form['seeking_venue_text']
    )
    if 'seeking_venue' not in request.form:
      artist.seeking_venue = False
    else:
      artist.seeking_venue = True
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  #PS
  shows = db.session.query(Show,Artist,Venue).join(Artist,Venue).all()
  data=[]
  for show in shows:
    data.append({
      "venue_id": show[2].id,
      "venue_name": show[2].name,
      "artist_id": show[1].id,
      "artist_name": show[1].name,
      "artist_image_link": show[1].image_link,
      "start_time": show[0].start_time.strftime("%m/%d/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  date_format = '%Y-%m-%d %H:%M:%S'
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = datetime.strptime(request.form['start_time'], date_format)
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    db.session.rollback()
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Show could not be listed.')
  else: 
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
