from flask import Flask,request,render_template,jsonify,flash,Response
from authlib.integrations.flask_client import OAuth
from flask import session,redirect,url_for,abort
from src.components.emotions_detection import Detect
from src.components.model_training import BuildModel
from src.components.youtube_data_scrap import you_scrap
from src.components.movies_recommend import Movies_session
from src.components.series_recommend import SeriesRecommend
from src.logger import logging
from src.utils import sqli_connect
import cv2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import date, datetime
import numpy as np
import warnings
warnings.filterwarnings('ignore')



app=Flask(__name__)

appConf = {
    "OAUTH2_CLIENT_ID": "255580419891-pvh0ikrmeov49d3hj7l2cls0mv8ieio3.apps.googleusercontent.com",
    "OAUTH2_CLIENT_SECRET": "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",
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": "ALongRandomlyGeneratedString",
    "FLASK_PORT": 5000
}

app.secret_key = appConf.get("FLASK_SECRET")
oauth = OAuth(app)

oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
    },
    server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}',
)


#==================Home page===================================
@app.route('/')
def sangeet():
    return render_template('front.html',session=session.get("user"))

@app.route('/about')
def about_details():
    return render_template('about.html',session=session.get("user"))

@app.route('/contact')
def contact_details():
    return render_template('contact.html',session=session.get("user"))

#================Login=========================================
@app.route("/sign-in-google")
def googleCallback():
    # fetch access token and id token using authorization code
    token = oauth.myApp.authorize_access_token()
    session["user"] = token
    return redirect(url_for("base"))

@app.route("/google-login")
def googleLogin():
    if "user" in session:
        abort(404)
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True))


@app.route("/logout")
def logout():
    session.pop("user", None)
    # return redirect(url_for("home"))
    return render_template('front.html',session=session.get("user"),user_data='')

@app.route('/login',methods=['GET','POST'])
def login_page():
    name=''
    password=''
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form.get('name')
        password = request.form.get('password')
    conn = sqli_connect('database')
    cursor = conn.cursor()
    query = "SELECT username, password from user_data where username='{usrname}' and password='{pswd}';".format(usrname=name,pswd=password)
    rows = cursor.execute(query)
    rows = rows.fetchall()
    if len(rows) == 1:
        flash(f"Hi {name}, welcome to Get Recommend")
        token = {'userinfo':{'name':name}}
        session['user'] = token
        return render_template('base.html',session = session.get('user'))
    else:
        message_alert = "Invalid username and password"
        flash(message_alert)
        return render_template('login.html',result = message_alert)


#==============register================================
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')  
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
    if password == confirm_password:   
        conn = sqli_connect('database')
        cursor = conn.cursor()     
        query = "INSERT INTO user_data VALUES('{u}','{e}','{p}');".format(u=username,e=email,p=password)
        try:
            cursor.execute(query)
            conn.commit()
            conn.close()
            flash("Registered Successfully")
            return render_template('register.html')
        except Exception as e:
            flash("User already exist")
            logging.info(f"{e}") 
            return render_template('register.html')
    else:
        flash("Password do not match with confirm password")
        return render_template('register.html') 
    
#=====================Dashboard===============================
@app.route('/dashboard')
def base():
    return render_template('base.html',session=session.get("user"))

@app.route('/show_div')
def show_div():
    return jsonify(success=True)
     
@app.route('/dashboard')
def home_page():
    return render_template('base.html')

@app.route('/myfunction')
def emotion_recommend():
    if request.method == 'POST':
        return render_template('songs.html')
    obj = BuildModel()
    train = "data/train"
    test = "data/test"
    train_generator,validation_generator,num_train,num_val,batch_size,num_epoch = obj.data_generation(train,test)      
    model = obj.model_creation()
    obj2 = Detect(model)
    emotion = obj2.display()
    final_emotion = emotion+" song"
    if final_emotion=="Sad song":
        final_emotion = "sad lofi song"
    obj3 = you_scrap()
    get_data = obj3.extract(final_emotion)
    return render_template('songs.html',data=get_data,session=session.get("user"))

#==================Song Recommend==========================================
@app.route('/songs')
def songs():
    return render_template('songs.html',session=session.get("user"))


#===============Movie Recommendation========================================

@app.route('/movie_recommend',methods=['GET','POST'])
def moive_suggestion():
    if request.method == 'GET':
        return render_template('base.html',session=session.get('user'))
    else:    
        obj = Movies_session()
        suggestions = obj.get_suggestions()
        return render_template('movies.html',suggestions=suggestions,session=session.get('user'))

@app.route("/populate-matches",methods=["POST"])
def populate_matches():
    # getting data from AJAX request
    res = json.loads(request.get_data("data"))
    movies_list = res['movies_list']

    movie_cards = {"https://image.tmdb.org/t/p/original"+movies_list[i]['poster_path'] if movies_list[i]['poster_path'] else "/static/images/movie_placeholder.jpeg": [movies_list[i]['title'],movies_list[i]['original_title'],movies_list[i]['vote_average'],datetime.strptime(movies_list[i]['release_date'], '%Y-%m-%d').year if movies_list[i]['release_date'] else "N/A", movies_list[i]['id']] for i in range(len(movies_list))}

    return render_template('recommend.html',movie_cards=movie_cards)

@app.route("/recommend",methods=["POST"])
def recommend():
    # getting data from AJAX request
    obj = Movies_session()
    clf = obj.clf_model
    vectorizer = obj.vectorizer
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    rel_date = request.form['rel_date']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    rec_movies_org = request.form['rec_movies_org']
    rec_year = request.form['rec_year']
    rec_vote = request.form['rec_vote']
    rec_ids = request.form['rec_ids']

    # get movie suggestions for auto complete
    suggestions = obj.get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies_org = obj.convert_to_list(rec_movies_org)
    rec_movies = obj.convert_to_list(rec_movies)
    rec_posters = obj.convert_to_list(rec_posters)
    cast_names = obj.convert_to_list(cast_names)
    cast_chars = obj.convert_to_list(cast_chars)
    cast_profiles = obj.convert_to_list(cast_profiles)
    cast_bdays = obj.convert_to_list(cast_bdays)
    cast_bios = obj.convert_to_list(cast_bios)
    cast_places = obj.convert_to_list(cast_places)
    
    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = obj.convert_to_list_num(cast_ids)
    rec_vote = obj.convert_to_list_num(rec_vote)
    rec_year = obj.convert_to_list_num(rec_year)
    rec_ids = obj.convert_to_list_num(rec_ids)
    
    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')

    for i in range(len(cast_chars)):
        cast_chars[i] = cast_chars[i].replace(r'\n', '\n').replace(r'\"','\"') 
    
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: [rec_movies[i],rec_movies_org[i],rec_vote[i],rec_year[i],rec_ids[i]] for i in range(len(rec_posters))}

    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    if(imdb_id != ""):
        # web scraping to get user reviews from IMDB site
        sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
        soup = bs.BeautifulSoup(sauce,'lxml')
        soup_result = soup.find_all("div",{"class":"text show-more__control"})

        reviews_list = [] # list of reviews
        reviews_status = [] # list of comments (good or bad)
        for reviews in soup_result:
            if reviews.string:
                reviews_list.append(reviews.string)
                # passing the review to our model
                movie_review_list = np.array([reviews.string])
                movie_vector = vectorizer.transform(movie_review_list)
                pred = clf.predict(movie_vector)
                reviews_status.append('Positive' if pred else 'Negative')

        # getting current date
        movie_rel_date = ""
        curr_date = ""
        if(rel_date):
            today = str(date.today())
            curr_date = datetime.strptime(today,'%Y-%m-%d')
            movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d')

        # combining reviews and comments into a dictionary
        movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}     

        # passing all the data to the html file
        return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
            vote_count=vote_count,release_date=release_date,movie_rel_date=movie_rel_date,curr_date=curr_date,runtime=runtime,status=status,genres=genres,movie_cards=movie_cards,reviews=movie_reviews,casts=casts,cast_details=cast_details)

    else:
        return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
            vote_count=vote_count,release_date=release_date,movie_rel_date="",curr_date="",runtime=runtime,status=status,genres=genres,movie_cards=movie_cards,reviews="",casts=casts,cast_details=cast_details)

#========================Series Recommend==========================================
@app.route('/home_series')
def series_suggestion():     
    obj = Movies_session()
    suggestions = obj.series_suggestion()
    return render_template('series.html',suggestions=suggestions,session= session.get('user'),data='',type='',you_id='',rec_data='')

@app.route('/series_matches',methods=['GET','POST'])
def series_matches():
    obj = Movies_session()
    suggestions = obj.series_suggestion() 
    if request.method=='GET':
        return render_template('series.html',sesion=session.get('user'),suggestions=suggestions,data='',type='',you_id='',rec_data='')
    else:
        title = request.form.get('name')
    obj2 = SeriesRecommend()
    info = obj2.match_extract(title)
    return render_template('series.html',data=info,session=session.get('user'),suggestions=suggestions,type='details_1',you_id='',rec_data='')

@app.route('/series_info',methods=['GET','POST'])
def series_info():
    obj = Movies_session()
    suggestions = obj.series_suggestion() 
    year = ''
    genre = ''
    rating = ''
    if request.method == 'GET':
        return render_template('series.html',sesion=session.get('user'),suggestions=suggestions,data='',type='',you_id='',rec_data='')
    else:
        year = request.form.get('year')
        genre = request.form.get('genre')
        rating = request.form.get('rating')    
    obj2 = SeriesRecommend()
    if year:    
        info = obj2.year_info(year)
    if genre:
        info = obj2.genre_info(genre)
    if rating:
        info = obj2.rating_info(rating)
    return render_template('series.html',data=info,type='details_1',session=session.get('user'),suggestions=suggestions,you_id='',rec_data='')    


@app.route('/series_recommend',methods=['GET','POST'])
def series_recommend():
    obj = Movies_session()
    suggestions = obj.series_suggestion() 
    if request.method == 'GET':
        return render_template('series.html',suggestions=suggestions,session=session.get('user'),data='',type='',you_id='',rec_data='')
    else:
        id = request.form.get('seriesId')   
    obj2 = SeriesRecommend()
    info = obj2.click_info(id)
    name = info[101]['name']
    recommended_data = obj2.getRecommendSeries(id) 
    obj3 = you_scrap()
    youtube_id = ''
    data_store = obj3.extract(name+" trailer")   
    for _,data in data_store.items():
        title = data['title'].lower()
        if "trailer" in title:
            youtube_id = data['id']
            break 
      
    return render_template('series.html',suggestions=suggestions,session=session.get('user'),data=info,type='details_2',you_id=youtube_id,rec_data=recommended_data)     

@app.route("/series-video")
def series_video():
    return render_template('series_recommend.html')
   

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)