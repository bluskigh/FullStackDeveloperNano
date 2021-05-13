#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from helpers import get_form_submission_info, upcoming_past_shows, provide_min_show, get_search_result
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

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
    """Returns all the venues with formatted data."""
    venues = db.session.query(Venue).all()
    areas = {}
    for venue in venues:
        city_state = f'{venue.city},{venue.state}' 
        venue_info = {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(venue.shows)}
        # if city is not in the areas dictionary 
        if not areas.get(city_state):
            # create a new key with a dictionary as its value
            areas[city_state] = {}
            # format the key (city) value with additional information 
            areas[city_state]['venues'] = []
        # append the venue_info to the to the city
        areas[city_state]['venues'].append(venue_info)
    return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', None)
    response = None
    if search_term:
        # uses a helper function (helpers.py) that searches the databbase for the search term(s) provided in the POST submission
        response = get_search_result(search_term, db.session, Venue)
    else:
        flash('Did not provide a search term.')
        return redirect('/venues')
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    """Shows the venue page with the given venue_id"""
    venue = db.session.query(Venue).get(venue_id)
    # getting the key/value pairs from the venue class instance
    data = venue.__dict__
    # adding upcoming / past shows to the venue
    upcoming_past_shows(data, venue.shows)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
@get_form_submission_info
def create_venue_submission(result_params):
    # unpacking key/value pair to create a new instance of Venue
    temp_venue = Venue(**result_params)
    try:
      db.session.add(temp_venue)
      db.session.commit()
      flash('Venue ' + temp_venue.name + ' was successfully listed!')
      return redirect('/venues')
    except Exception as e:
      # for stack trace
      print(e)
      db.session.rollback()
      flash('An error occurred. Venue ' + temp_venue.name + ' could not be listed.')
      return redirect('/venues/create')

    return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # getting an instance of the artist
    artist = db.session.query(Artist).get(artist_id)
    try:
        # pending deletion to our transaction
        db.session.delete(artist)
        db.session.commit()
        flash(f'{artist.name} deleted.')
        return jsonify({'result': True})
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(f'{artist.name} NOT deleted.')
        return jsonify({'result': False})

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = db.session.query(Venue).get(venue_id)
    if not venue:
      flash("Invalid venue_id given.")
      return jsonify({'result': False})
    
    try:
      db.session.delete(venue)
      db.session.commit()
      flash(f'{venue.name} deleted.')
      return jsonify({'result': True})
    except Exception as e:
      db.session.rollback()
      flash(f'Could not delete venue: {venue_id}.')
      return jsonify({'result': False})

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    data = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '');
    response = None
    if search_term:
        response = get_search_result(search_term, db.session, Artist)
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = db.session.query(Artist).get(artist_id)
    # get key value pair of variables and values in the current instance of the class 
    data = artist.__dict__
    upcoming_past_shows(data, artist.shows)
    return render_template('pages/show_artist.html', artist=artist)

# sends back availability restriction information of the artist
@app.route('/artists/<int:artist_id>/get_availability')
def get_availability(artist_id):
    """Send back availability restriction information of the artist.""" 
    artist = db.session.query(Artist).get(artist_id)
    message = {'exist': True, 'id': artist_id, 'available': True}
    if not artist:
        message['exist'] = False
        return jsonify(message)
    # check whether the artist is available for booking
    if not artist.seeking_venue:
        message['available'] = False
        return jsonify(message)
    if artist.availability_restriction:
        message['restriction'] = True
        message['from_time'] = artist.from_time 
        message['to_time'] = artist.to_time
    else:
        message['restriction'] = False
    return jsonify(message)

@app.route('/artists/<int:artist_id>/available', methods=['POST'])
def is_artist_available(artist_id):
    """Checks if the start_time given fits the availability restriction of the artist."""
    artist = db.session.query(Artist).get(artist_id)
    message = {'id': artist_id}

    message['available'] = True 

    start_time = request.get_json()['start_time']
    if artist.availability_restriction:
        try:
            # in order to compare need datetime object from start_time string
            start_time = datetime.fromisoformat(start_time)
            if start_time < datetime.fromisoformat(artist.to_time) and start_time > datetime.fromisoformat(artist.from_time):
                message['valid'] = True
                return jsonify(message)
            else:
                message['choosen_time'] = start_time
                message['valid'] = False
                return jsonify(message)
        except ValueError as e:
            message['choosen_time'] = start_time
            message['valid'] = False
            return jsonify(message)
    else:
        return jsonify({'valid': True, 'choosen_time': start_time})

@app.route("/venues/<int:venue_id>/exist")
def venue_exist(venue_id):
    venue = db.session.query(Venue).get(venue_id)
    if not venue:
        return jsonify({'exist': False, 'id': venue_id})
    return jsonify({'exist': True, 'id': venue_id})

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id, **kwargs):
    form = ArtistForm()
    # get artist that is trying to be updated
    artist = db.session.query(Artist).get(artist_id)
    # populate form with fields from artist with ID <artist_id>
    form.name.render_kw = {'value': artist.name}
    form.city.render_kw = {'value': artist.city}
    form.phone.render_kw = {'value': artist.phone}
    form.image_link.render_kw = {'value': artist.image_link}
    form.facebook_link.render_kw = {'value': artist.facebook_link}
    form.website_link.render_kw = {'value': artist.website}
    form.seeking_description.render_kw = {'value': artist.seeking_description}
    # default processed after form is instantiated, so doing: form.default has no effect, thus need to change via data attribute 
    form.availability_restriction.data = artist.availability_restriction
    form.genres.data = artist.genres
    form.seeking_venue.data = artist.seeking_venue
    form.state.data = artist.state
    # if the artist contains from_time / to_time
    if artist.availability_restriction:
        form.from_time.render_kw = {'value': artist.from_time}
        form.to_time.render_kw = {'value': artist.to_time}
    else:
        # provide current time as defaults
        form.from_time.render_kw = {'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        form.to_time.render_kw = {'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
@get_form_submission_info
def edit_artist_submission(artist_id, result_params):
    """Updates artist based on POST submission body"""
    try:
        # update only the artist that has an id of artist_id
        db.session.query(Artist).filter(Artist.id==artist_id).update(result_params)
        # save updates 
        db.session.commit()
        flash(f'Updated artist with account id of: {artist_id}')
        return redirect(url_for('show_artist', artist_id=artist_id))
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(f'Could not update artist with id of: {artist_id}')
        return redirect(f'/artists/{artist_id}/edit')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    """Renders form to edit"""
    form = VenueForm()
    # get artist that is trying to be updated
    venue = db.session.query(Venue).get(venue_id)
    # populate form with fields from artist with ID <artist_id>
    form.name.render_kw = {'value': venue.name}
    form.city.render_kw = {'value': venue.city}
    form.phone.render_kw = {'value': venue.phone}
    form.image_link.render_kw = {'value': venue.image_link}
    # default processed after form is instantiated, so doing: form.default has no effect, thus need to change via data keyword
    form.facebook_link.render_kw = {'value': venue.facebook_link}
    form.website_link.render_kw = {'value': venue.website}
    form.seeking_description.render_kw = {'value': venue.seeking_description}
    form.address.render_kw = {'value': venue.address}

    form.seeking_talent.data = venue.seeking_talent
    form.genres.data = venue.genres
    form.state.data = venue.state

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
@get_form_submission_info
def edit_venue_submission(venue_id, result_params):
    """Updates venue based on POST submission body."""
    # venue record with ID <venue_id> using the new attributes
    try:
        db.session.query(Venue).where(Venue.id==venue_id).update(result_params)
        db.session.commit()
        flash(f'Updated venue: {result_params.get("name")}')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while trying to update venue: {result_params.name}')
        return redirect(f'/venues/{venue_id}')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
@get_form_submission_info
def create_artist_submission(result_params):
    """Creates a new artist based on POST submission body."""
    try:
      # unpacking result_params to create a new instance of Artist
      temp_actor = Artist(**result_params)
      db.session.add(temp_actor)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + temp_actor.name + ' was successfully listed!')
      return render_template('pages/home.html')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist ' + temp_actor.name + ' could not be listed.')
      return redirect('/artists/create')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    """
    Shows all upcoming shows.
    """
    data = db.session.query(Show).all()
    # ("Show" by default only contains a start_time, but it has a relationship which links the "Show" to its relative Artist/Venue. So, provide_min_show() takes advantage of that and formats the data relative to the provided default data given in the starter code.)
    data = [provide_min_show(show) for show in data if datetime.fromisoformat(show.start_time) > datetime.now()]
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    aid = request.form.get('artist_id')
    vid = request.form.get('venue_id')
    st = request.form.get('start_time')

    if not aid or not vid or not st:
        flash('Did not insert necessary inputs')
        return redirect('/shows/create')

    artist = db.session.query(Artist).get(aid)
    if not artist.seeking_venue:
        flash('This artist is not currently available for booking.')
        return redirect('/shows/create')
    if not artist:
        flash('Artist id is invalid.')
        return redirect('/venues/create')
    venue = db.session.query(Venue).get(vid)
    if  not venue:
        flash('Venue id is invalid.')
        return redirect('/shows/create')

    try:
        # check if proper iso format was given (when converting to datetime object, if invalid iso format given a ValueError is raised, we catch.)
        datetime.fromisoformat(st)
        if artist.availability_restriction:
            start_time = datetime.fromisoformat(st)
            if start_time > datetime.fromisoformat(artist.to_time) or start_time < datetime.fromisoformat(artist.from_time):
                flash('Start time did not meet artist availability restriction criteria')
                return redirect('/shows/create')
        temp_show = Show(start_time=st)
        db.session.add(temp_show)
        artist.shows.append(temp_show)
        venue.shows.append(temp_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return redirect('/shows')
    except ValueError:
        flash('Did not provide proper iso format date')
        return redirect('/shows/create')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        # return render_template('pages/home.html')
        return redirect('/shows/create')

#----------------
# Error handlers
#----------------
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
