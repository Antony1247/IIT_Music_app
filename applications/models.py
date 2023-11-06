from applications.database import db

class Users(db.Model):
	__tablename__ = 'users'
	user_id =db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
	username =db.Column(db.String(80), unique=True, nullable=False)
	password=db.Column(db.String(120), nullable=False)
	name=db.Column(db.String(80), nullable=False)

class Artists(db.Model):
	__tablename__ = 'artists'
	artist_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
	name = db.Column(db.String(80), nullable=False)
	biography = db.Column(db.Text(1000), nullable=False)
	birth_date = db.Column(db.Date, nullable=False)
	country=db.Column(db.String(80), nullable=False)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.Text, nullable=False)

	albums = db.relationship("Albums", back_populates="artist")

class Albums(db.Model):
	__tablename__ = 'albums'
	album_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
	title = db.Column(db.String(80), nullable=False)
	release_date = db.Column(db.Date)
	genre = db.Column(db.Text)
	cover = db.Column(db.LargeBinary, nullable=False) 
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'), nullable=False)

	artist = db.relationship("Artists", back_populates="albums")
	songs = db.relationship("Songs", back_populates="album")

class Songs(db.Model):
	__tablename__ = 'songs'
	song_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
	title = db.Column(db.String(80), nullable=False)
	duration = db.Column(db.Integer)
	album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'), nullable=False)
	lyrics = db.Column(db.Text, nullable=False)
	song = db.Column(db.LargeBinary, nullable=False)  # BLOB column to store MP3 data
	cover = db.Column(db.LargeBinary, nullable=False)  # BLOB column to store cover image data
	album = db.relationship("Albums", back_populates="songs")