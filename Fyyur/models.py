from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# creates a many-to-many relationship between a venue and show
venue_show_bridge = db.Table('venue_show', db.Column('venue_id', db.Integer, db.ForeignKey(
    'venues.id')), db.Column('show_id', db.Integer, db.ForeignKey('shows.id')))
# creates a many-to-many relationship between an artist and a show
artist_show_bridge = db.Table('artist_show', db.Column('artist_id', db.Integer, db.ForeignKey(
    'artists.id')), db.Column('show_id', db.Integer, db.ForeignKey('shows.id')))

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))

    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))

    shows = db.relationship('Show', secondary=venue_show_bridge, backref=db.backref(
        'venue', lazy=True, uselist=False), cascade='all, delete')


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)

    shows = db.relationship('Show', secondary=artist_show_bridge, backref=db.backref(
        'artist', lazy=True, uselist=False), cascade='all, delete')

    # availability restriction 
    availability_restriction = db.Column(db.Boolean, nullable=False)
    to_time = db.Column(db.String)
    from_time = db.Column(db.String)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    # artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    # venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))


