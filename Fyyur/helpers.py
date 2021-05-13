from functools import wraps
from flask import request, session, redirect, flash
from datetime import datetime
from forms import ArtistForm, VenueForm

def get_form_submission_info(func):
    # save original information from function being decorated 
    @wraps(func)
    def form_info_wrapper(*args, **kwargs):
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        facebook = request.form.get('facebook_link')
        image = request.form.get('image_link')
        website = request.form.get('website_link')
        seeking_description = request.form.get('seeking_description')

        result_params = {'name': name, 'city': city, 'state': state, 'phone': phone, 'facebook_link': facebook, 'image_link': image, 'website': website, 'seeking_description': seeking_description}

        form = None
        # special values that require more than just request.form.get(...)
        if 'artists' in request.path: 
            form = ArtistForm()
            result_params['seeking_venue'] = form.seeking_venue.data 
            # availability restriction
            result_params['availability_restriction'] = form.availability_restriction.data 
            if result_params.get('availability_restriction'):
                try:
                    result_params['from_time'] = request.form.get('from_time');
                    datetime.fromisoformat(result_params['from_time'])
                    result_params['to_time'] = request.form.get('to_time');
                    datetime.fromisoformat(result_params['to_time'])
                except ValueError:
                    flash('Did not provide a proper iso format date')
                    return redirect(f'/artists')
        elif 'venues' in request.path:
            form = VenueForm()
            result_params['seeking_talent'] = form.seeking_talent.data 
            result_params['address'] = address

        # universal for Artist/Venue, but needs a form to be defined first
        result_params['genres'] = form.genres.data
        # final result
        kwargs['result_params'] = result_params
        # get the original execution, so call with original parameters
        return func(*args, **kwargs)
    return form_info_wrapper

def upcoming_past_shows(data, shows):
    """
    Modified the given dictionary to contain upcming/past shows (and count) keys.
    Compares the show start time to current time of the user visiting the page.
    If the show has a greater time then it will be placed in upcoming.
    It the show is lower then it will be placed in past.
    ISO formatting is used.
    """
    upcoming = [provide_min_show(show) for show in shows if datetime.fromisoformat(show.start_time) > datetime.now()]
    past = [provide_min_show(show) for show in shows if datetime.fromisoformat(show.start_time) < datetime.now()] 
    # added properties that are not in the model (Artist or Venue) itself.
    data['upcoming_shows_count'] = len(upcoming)
    data['upcoming_shows'] = upcoming
    data['past_shows_count'] = len(past)
    data['past_shows'] = past

def provide_min_show(show):
    """ 
    Provides minimal information about a certain show.
    - formatting inspired by the data given in starter code.
    """
    return {'artist_image_link': show.artist.image_link, 'start_time': show.start_time, 'artist_id': show.artist.id, 'artist_name': show.artist.name, 'venue_id': show.venue.id, 'venue_name': show.venue.name, 'venue_image_link': show.venue.image_link}

def get_search_result(search_term, session, Model):
    """
    Model = Artist / Venue
    Queries through all possible Model items. First gets a general query, which is a query that contains a word in the search term, then attempts to minimize the search but looking for more terms in the general query.
    """
    # will be returned with possible data
    response = None
    if search_term:
        general_query = None
        # split the search_terms by spaces
        terms = search_term.split(' ')
        for term in terms:
            term = f'%{term}%'
            if general_query:
                # get a more specific search result
                temp = general_query.filter(Model.name.ilike(term))
                if temp.first():
                    general_query = temp
            else:
                # get a generic search
                temp = session.query(Model).filter(Model.name.ilike(term))
                if temp.first():
                    general_query = temp

        if general_query:
            response = {}
            # populating data key with array of results from search
            response['data']  = general_query.all()
            # formating the populated data
            response['data'] = [
                    {'id': venue.id, 
                    'name': venue.name, 
                    'num_upcoming_shows': len(venue.shows)
                    } for venue in response.get('data')]
            # setting count of search result
            response['count'] = len(response.get('data'))
    return response 
