from flask import abort,redirect,render_template , url_for,flash, request,jsonify
from PIL import Image
from cms.forms import UpdateForm,RegistrationForm,LoginForm,PostForm,FeedbackForm
from cms import app,mongo,bcrypt, login_manager
from flask_login import login_user,current_user,logout_user,login_required
from cms.models import User
import datetime,secrets
import pymongo,os
from bson import ObjectId
records =mongo.db.users

def save_picture(from_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext = os.path.splitext(from_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path,'static\profilepics',picture_fn)
    output_size = (125,125)
    i = Image.open(from_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/home")
@login_required
def home():
    fav=mongo.db.favourite
    curr_user = records.find_one({'_id': current_user._id})
    posts=  mongo.db.post.find().sort([("_id", -1)])
    return render_template('home.html', posts=posts,curr_user=curr_user,fav=fav)

@app.route("/myposts")
@login_required
def myposts():
    fav=mongo.db.favourite
    curr_user = records.find_one({'_id': current_user._id})
    posts=  mongo.db.post.find({'user_id': current_user._id}).sort([("_id", -1)])
    return render_template('myposts.html', posts=posts,curr_user=curr_user,fav=fav)

@app.route("/fav_posts_list")
@login_required
def fav_posts_list():
    curr_user = records.find_one({'_id': current_user._id})
    fav=mongo.db.favourite
    database=mongo.db.post
    fav_list = mongo.db.favourite.find({'user_id': current_user._id}).sort([("_id", -1)])
    postnumber = fav_list.count()
    if fav_list:
        output=[]
        for post in fav_list:
            post_id= post['post_id']
            post = mongo.db.post.find_one({'_id': post['post_id']})
            output.append(post)
    else:
        flash(f'Your dont have favourite posts.','success')
        return redirect(url_for('account'))
    return render_template('fav_list.html', output=output,curr_user=curr_user,fav=fav,postnumber=postnumber)
    
@app.route("/")
@app.route("/about", methods=['GET','POST'])
def about():
    form = FeedbackForm()
    if current_user.is_authenticated:
        user=records.find_one({'_id': current_user._id})
        username=user['username']
        form.user.data=username
    if form.validate_on_submit():
        mongo.db.feedback.insert({ "feedback":form.feedback.data})
        flash(f'Your feedback has been sent!','success')
        return redirect(url_for('about'))
    return render_template('about.html',legend='Feedback form',title='Feedback',form=form)

    

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        records.insert({ "username":form.username.data, "email":form.email.data, "password":hashed_password,"role":form.role.data,'picture':picture_file})
        flash(f'Your account has been created.Now you can log in.','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = records.find_one({'email': form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            user_obj = User(user['username'])
            login_user(user_obj)
            next_page=request.args.get('next')
            flash('You have been loged in!','success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Please check your email or password','danger')
    return render_template('login.html',title='Login',form=form)
        
@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    user = records.find_one({'_id': current_user._id})
    form = PostForm()
    if (user['role'] == 'author'):
        if form.validate_on_submit():
            mongo.db.post.insert({ "author":user, "title":form.title.data,"date_posted":datetime.datetime.now(),"content":form.content.data})
            flash(f'Your post has been created!','success')
            return redirect(url_for('home'))
    else:
        abort(403)

    return render_template('create_post.html',legend='New Post',title='New Post',form=form)


    

@app.route("/post/<_id>")
def post(_id):
    fav=mongo.db.favourite
    post=mongo.db.post.find_one({'_id':ObjectId(_id)})
    curr_user = records.find_one({'_id': current_user._id})
    return render_template('post.html', title=post['title'],post=post,curr_user=curr_user,fav=fav)

@app.route("/post/<_id>/update",methods=['GET','POST'])
def update_post(_id):
    form = PostForm()
    post=mongo.db.post.find_one({'_id':ObjectId(_id)})
    user = records.find_one({'_id': current_user._id})
    if post['author'] != user['username']:
        abort(403)
    if form.validate_on_submit():
        mongo.db.post.update_one({'_id': ObjectId(_id)}, {'$set': {"title":form.title.data, "content":form.content.data}})
        flash('Your post has been updated!','success')
        return redirect(url_for('post',_id=post['_id']))
    elif request.method== 'GET':
        form.title.data =post['title']
        form.content.data =post['content']
    return render_template('create_post.html',title='Update Post',legend='Update Post',form=form,post=post)

@app.route("/post/<_id>/delete",methods=['POST'])
@login_required
def delete_post(_id):
    post=mongo.db.post.find_one({"_id":ObjectId(_id)})
    user = records.find_one({"_id": current_user._id})
    if (post['author'] == user['username']) or (user['role'] =='admin'):
        # fav_listed= db.favourite.find({"post_id":ObjectId(_id)})
        # if fav_listed:
        #     for data in fav_listed:
        #         db.favourite.delete_one({"_id": data['_id']})
        mongo.db.favourite.delete_many({"post_id": ObjectId(_id)})      
        mongo.db.post.delete_one({"_id": ObjectId(_id)})
        flash('Your post has been deleted!','success')
        return redirect(url_for('home'))
    else:
        abort(403)

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form=UpdateForm()
    user = records.find_one({'_id': current_user._id})
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            mongo.db.users.update_one({'_id': current_user._id}, {'$set': { "picture":picture_file}})
        mongo.db.users.update_one({'_id': current_user._id}, {'$set': {"username":form.username.data, "email":form.email.data}})
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method== 'GET':
        form.username.data =user['username']
        form.email.data =user['email']
    return render_template('account.html',title='account',user=user,form=form)

@app.route("/user/<username>")
@login_required
def user_posts(username):
    fav=mongo.db.favriout
    posts=  mongo.db.post.find({'author': username}).sort( [("_id", -1)]   )
    curr_user = records.find_one({'_id': current_user._id})
    postnumber=posts.count()
    return render_template('user_posts.html', posts=posts,username=username,postnumber=postnumber,curr_user=curr_user,fav=fav)

@app.route("/is_favourite_post/<_id>/<path>",methods=['GET','POST'])
def is_favourite_post(_id,path):
    mongo.db.favourite.insert({ "user_id":current_user._id, "post_id":ObjectId(_id),"IsFavourite":True})
    return redirect(url_for(path))

@app.route("/not_favourite_post/<_id>/<path>",methods=['GET','POST'])
def not_favourite_post(_id,path):
    mongo.db.favourite.delete_one({ "user_id":current_user._id,"post_id":ObjectId(_id)})
    return redirect(url_for(path))   

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('about'))
 
    

    
  