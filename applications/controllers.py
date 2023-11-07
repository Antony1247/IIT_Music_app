import os
import io
from io import BytesIO
from flask import Flask, redirect , send_file, Response
from flask import render_template
from flask import request,url_for,flash
from flask import current_app as app
from applications.models import *
from applications.database import db
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image

@app.route('/', methods=['GET', 'POST'])
def select():
	return render_template('select.html')
	

##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## CREATING NEW USER / ARTIST
	
@app.route('/aregister', methods=['GET', 'POST'])
def new_artist():
	if request.method == 'POST':
		username = request.form.get('username')
		password= request.form.get('password')
		name= request.form.get('name')
		biography= request.form.get('biography')
		birth_date_str=request.form.get('birth_date')
		country= request.form.get('country')

		birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

		new_user = Artists(name=name,biography=biography,birth_date=birth_date,country=country,username=username, password=password)
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('artist_login'))	
	else:
		return render_template('artist-registration.html')
	
@app.route('/register', methods=['GET', 'POST'])
def new_user():
	if request.method == 'POST':
		username1 = request.form.get('newusername')
		password1= request.form.get('newpassword')
		name1= request.form.get('fullname')
		new_user = Users(username=username1, password=password1, name=name1)
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('user_login'))	
	else:
		return render_template('user-registration.html')
	


##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## LOGIN OPERATIONS

@app.route('/user', methods=['GET', 'POST'])
def user_login():
	username = None
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		name = db.session.query(Users).filter(Users.username==username, Users.password==password).first()
		if name:
			return render_template('options1.html',user=name)
		else:
			return render_template('error_password.html')
	else:
		return render_template('user-login.html')

@app.route('/artist', methods=['GET', 'POST'])
def artist_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        artist = db.session.query(Artists).filter(Artists.username == username, Artists.password == password).first()
        if artist:
            # Redirect to the artist's profile page using their artist_id
            return redirect(url_for('artist_profile', artist_id=artist.artist_id))
        else:
            return render_template('error_password.html')
    else:
        return render_template('artist-login.html', artist=None)  # artist=None because it's not defined here



##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## VIEW OPERATIONS

@app.route('/artist/<int:artist_id>/home')
def artist_profile(artist_id):
    # Fetch the artist's data using artist_id and display their profile
    artist = db.session.query(Artists).filter(Artists.artist_id == artist_id).first()
    songs = Songs.query.all()
    return render_template('artist.html', songs=songs, artist=artist)

@app.route('/artist/<int:artist_id>/albums')
def artist_albums(artist_id):
    # Fetch the artist's data using artist_id and display their profile
	albums = db.session.query(Albums).filter(Albums.artist_id == artist_id).all()
	artist1 = db.session.query(Artists).filter(Artists.artist_id == artist_id).first()
	return render_template('album_list.html', albums=albums, artist=artist1)

@app.route('/artist/<int:artist_id>/albums/<int:album_id>/<title>')
def artist_albums_songs(artist_id,album_id,title):
    # Fetch the artist's data using artist_id and display their profile
	albums = db.session.query(Albums).filter(Albums.album_id == album_id).first()
	artist1 = db.session.query(Artists).filter(Artists.artist_id == artist_id).first()
	songs= db.session.query(Songs).filter(Songs.album_id == album_id).all()
	return render_template('album_song_list.html', albums=albums, artist=artist1, songs=songs)



##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## ALBUM OPERATIONS 

@app.route('/artist/<artist_id>/albums/addalbum', methods=['GET', 'POST'])
def add_album(artist_id):
	artist = Artists.query.get(artist_id)  # Use SQLAlchemy's get method to retrieve the artist

	if request.method == 'POST':
		title = request.form.get('title')
		release_date_str = request.form.get('release_date')
		genre = request.form.get('genre')
		cover = request.files['cover']
		
		release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
		if cover and allowed_image_file(cover.filename):
			cover_image_binary = cover.read()
			
			new_album = Albums(title=title, release_date=release_date, genre=genre, cover=cover_image_binary, artist_id=artist_id)

			db.session.add(new_album)
			db.session.commit()

			return redirect(url_for('artist_albums', artist_id=artist_id))
		else:
			flash('Invalid file types. Please upload an allowed image for the cover.')
			return redirect(request.url)

	return render_template('add_album.html', artist=artist)

@app.route('/artist/<int:artist_id>/albums/<int:album_id>/<title>/update', methods=['GET', 'POST'])
def album_update(artist_id,album_id,title):
	artist = db.session.query(Artists).filter(Artists.artist_id == artist_id).first()
	album = Albums.query.get_or_404(album_id)

	if request.method == 'POST':
		album.title = request.form['title']
		release_date_str = request.form['release_date']
		album.genre = request.form['genre']

		album.release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
		if 'cover' in request.files:
			cover_data = request.files['cover'].read()
			album.cover = cover_data
        
		db.session.commit()
		return redirect(url_for('artist_albums', artist_id=artist_id))
	else:
		return render_template('update_album.html', artist=artist, album=album)

@app.route('/artist/<int:artist_id>/albums/<int:album_id>/<title>/delete', methods=['GET', 'POST'])
def delete_album(artist_id,album_id,title):
	album = Albums.query.get_or_404(album_id)
	if request.method == 'POST':
		del_id = request.form['id']
		del_album = Albums.query.filter_by(album_id=del_id).first()
		del_song = db.session.query(Songs).filter(Songs.album_id==del_id).all()
		for del1 in del_song:
			db.session.delete(del1)
		db.session.delete(del_album)
		db.session.commit()
		return redirect(url_for('artist_albums',artist_id=artist_id))
	else:
		return render_template('delete_confirmation_album.html', album=album)


##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## SONG OPERATIONS

@app.route('/artist/<int:artist_id>/albums/<int:album_id>/<title>/<int:song_id>/update', methods=["GET", "POST"])
def update_song(artist_id, album_id, title, song_id):
    artist = db.session.query(Artists).filter(Artists.artist_id == artist_id).first()
    song = Songs.query.get_or_404(song_id)

    if request.method == 'POST':
        song.title = request.form['title']
        song.duration = request.form['duration']
        song.lyrics = request.form['lyrics']

        if 'song_data' in request.files:
            song_data = request.files['song_data'].read()
            song.song = song_data

        if 'cover_image' in request.files:
            cover_data = request.files['cover_image'].read()
            song.cover = cover_data
        
        db.session.commit()
        return redirect(url_for('artist_albums_songs', artist_id=artist_id, album_id=album_id, title=title))
    else:
        return render_template('update_song.html', artist=artist, song=song)

@app.route('/artist/<int:artist_id>/albums/<album_id>/<title>/<int:song_id>/delete', methods=["GET", "POST"])
def delete_song(artist_id,album_id,title,song_id):
	song = Songs.query.get_or_404(song_id)
	if request.method == 'POST':
		del_id = request.form['id']
		del_song = Songs.query.filter_by(song_id=del_id).first()
		db.session.delete(del_song)
		db.session.commit()
		return redirect(url_for('artist_albums_songs',artist_id=artist_id,album_id=album_id,title=title))
	else:
		return render_template('delete_confirmation_song.html', song=song)

@app.route('/artist/<artist_id>/albums/<album_id>/<title>/addsong', methods=['GET', 'POST'])
def add_song(artist_id,album_id,title):
	artist = db.session.query(Artists).filter(Artists.artist_id == artist_id).first()
	if request.method == 'POST':
		title = request.form.get('title')
		duration = request.form.get('duration')
		lyrics = request.form.get('lyrics')
		song_data = request.files['song_data']
		cover_image = request.files['cover_image']

		if song_data and allowed_file(song_data.filename) and cover_image and allowed_image_file(cover_image.filename):
            # Ensure that the uploaded files are of the allowed types (e.g., mp3 for songs and image for cover)
			song_data_binary = song_data.read()
			cover_image_binary = cover_image.read()

            # Create a new Song object and populate its fields
			new_song = Songs(title=title, duration=duration, album_id=album_id, lyrics=lyrics, song=song_data_binary, cover=cover_image_binary)

            # Add the new song to the database and commit the transaction
			db.session.add(new_song)
			db.session.commit()
			return redirect(url_for('artist_albums_songs', artist_id=artist_id, album_id=album_id, title=title))
		else:
			flash('Invalid file types. Please upload an MP3 song and an image for the cover.')
			return redirect(request.url)

	return render_template('addsong.html', artist=artist)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}
def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}



##PLAY SONG------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/artist/<int:song_id>/serve_image')
def get_image(song_id):
    song = Songs.query.get(song_id)
    if song and song.cover:
        image = Image.open(BytesIO(song.cover))
        response = BytesIO()
        image.save(response, format="JPEG")
        response.seek(0)
        return send_file(response, mimetype='image/jpeg')

    return 'Image not found', 404

@app.route('/artist/<int:song_id>/serve_audio')
def serve_audio(song_id):
    song = Songs.query.get(song_id)

    if song and song.song:
        binary_audio_data = BytesIO(song.song)  # Assuming 'song.song' is the binary audio data

        # Serve the binary audio data with the correct MIME type
        return send_file(binary_audio_data, mimetype='audio/mpeg', as_attachment=False)

    return "Song not found", 404

# This route renders the HTML template for playing audio.
@app.route('/artist/<int:song_id>/play')
def play_audio(song_id):
    song = Songs.query.get(song_id)
    
    if song:
        audio_url = url_for('serve_audio', song_id=song_id)
        cover_url = url_for('get_image', song_id=song_id)
        return render_template('song_player.html', audio_url=audio_url, song=song, cover_url=cover_url)

    return "Song not found", 404

