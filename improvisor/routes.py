from flask_wtf import FlaskForm
from flask_wtf.file import FileField
import os
from os.path import join
from improvisor.forms import FormTag, FormSignup, FormAsset, FormLogin
from improvisor.models.tag_model import TagModel
from improvisor.models.user_model import UserModel
from improvisor.models.asset_model import AssetModel
from flask import Flask, render_template, request, redirect, jsonify, session, abort
from improvisor import app, socketio, sample_files
from operator import itemgetter
import json
import copy



#API: inserts tag into database
@app.route('/api/tag', methods=['GET','POST'])
def addTag():
    form = FormTag(request.form)
    if (session["logged_in"] == False): #A valid user must be logged in before a tag can be added to db
        print("No user is logged in. won't add tag")
        error ="User must be logged in to add a tag" #I don't really know how to use these error things for the flask forms Alex
        return render_template ("tag_form.html", form = form, error = error)
    
    if form.validate() and request.method=="POST":
        print("Valid form submitted: " + form.tag.data)
        tag = TagModel(form.tag.data, session["user_id"]) #creates tag database object
        try:
            tag.save_to_db()
        except:
            error = "Error while saving to db"
            return render_template('tag_form.html', form=form, error = error)
        return redirect('/')
    return render_template('tag_form.html', form=form)

#API: extracts all of the current user's tags from the database returning a json 
@app.route('/api/user_tags_list', methods=['GET'])
def getTags():
    if session["logged_in"] == True:
        return jsonify({"tags":[tag.json() for tag in TagModel.query.filter_by(user_id = session["user_id"]).all()]})
    else:
        print("No user is logged in, can't get tags")
        return redirect('/')


#API: inserts user into database
@app.route('/api/userRegister', methods=['GET','POST'])
def addUser():
    form = FormSignup(request.form)
    if (request.method=="POST" and form.validate()):
        print(f'Valid form submitted Firstname: {form.firstname.data} Lastname: {form.lastname.data} Email: {form.email.data} ')
        user = UserModel(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
        try: 
            user.save_to_db()
        except: 
            error = "Error while saving user to db"
            return render_template('signup.html', form=form, error=error)
        return redirect('/')
    return render_template('signup.html', form=form)

#API: gets user from database and updates session dictionary -- not secure yet
@app.route('/api/login', methods=["GET", "POST"])
def loginUser():
    form = FormLogin(request.form)
    if (request.method == "POST" and form.validate()):
        print(f"valid form submitted {form.email.data} and {form.password.data}")
        user = UserModel.find_by_email(form.email.data)
        if user:
            session["user_id"] = user.id
            session["logged_in"] = True
            print(f'logged in as {user.email} with id {session["user_id"]}')
            return redirect('/')
        else:
            error = "Invalid credentials"
            return(render_template('login.html', form = form, error = error))
    return (render_template('login.html', form= form))

#API: extracts all users from database
@app.route('/api/userList', methods=['GET'])
def getUsers():
    return jsonify({"users": [user.json() for user in UserModel.query.all()]})

#API: given a tag, returns a list of the user's assets containing that tag
@app.route('/api/assets_with_tag', methods=['GET'])
def getAssets():
    phrase = request.form.get('phrase')
    mentioned_tags = request.form.get("mentionedTags")
    tag = TagModel.find_by_tagName(phrase)
    if tag:
        return {"assets-with-tag" : [asset.json() for asset in tag.assets]}
    else: 
        return {"message" : "Tag does not exist in database"}
    #if not mentioned_tags:
        #mentioned_tags = {"recent" : {},
           # }

#API: returns all assets in the database
@app.route('/api/all_assets', methods=["GET"])
def allAssets():
    print("all_assets")
    return jsonify({"assets" : [asset.json() for asset in AssetModel.query.all()]})


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        print("uploading")
        theFile= request.files['inputFile']
        os.mkdir("uploadedFiles")
        save_location = join("uploadedFiles", theFile.filename )
        open(save_location, "w")
        return theFile.filename
    return render_template("asset_form.html")


#API: inserts asset into database and allows tags to be added to asset
@app.route('/api/asset', methods=["GET", "POST"])
def addAsset():
    form = FormAsset(request.form)
    if (session["logged_in"] == False): #A valid user must be logged in before an asset can be added to db
        print("No user is logged in. won't add asset")
        error ="User must be logged in to add a asset" 
        return render_template ("asset_form.html", form = form, error = error)

    if (request.method=="POST" and form.validate()):
        print(f'Valid form submitted Asset-name is : {form.assetname.data}')
        
        asset = AssetModel.find_by_assetName(form.assetname.data) #tries to retrieve asset from database
        if asset:   
            if form.tagname.data: #if the asset already exists then try to add a tag to it
                print (form.tagname.data)
                tag = TagModel.find_by_tagName(form.tagname.data)
                if tag:
                    asset.tags.append(tag)
            else:
                print("asset already exists") #if no tag is entered then there is nothing to update 
                return render_template("asset_form.html", form=form)
        else:
             asset = AssetModel(form.assetname.data, session["user_id"]) #if there is no asset in database then create it and check for possible tag entry 
             if form.tagname.data:
                tag = TagModel.find_by_tagName(form.tagname.data)
                if tag:
                    asset.tags.append(tag)
        try:
            asset.save_to_db()
        except:
            error = "Error while saving asset to db"
            return render_template("asset_form.html", form=form, error=error)
        return redirect('/')
    return render_template("asset_form.html", form=form )
    
        


# Retrieve the sample assets from sample_files.py
assets = sample_files.assets


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/fetch_tagset', methods=['GET'])
def fetch_tagset():
    tag_pool = []
    for asset in assets:
        for tag in asset['tags']:
            if tag not in tag_pool:
                tag_pool.append(tag)
    return json.dumps(tag_pool)

@app.route('/join_session', methods=['GET'])
def enter_session():
    return render_template('enter_session.html')

@app.route('/presenter', methods=['GET'])
def presenter_view():
    return render_template('presenter.html')

@app.route('/controller', methods=['GET'])
def controller_view():
    return render_template('controller.html')

@app.route('/user_settings', methods=['GET', 'POST'])
def user_settings_view():
    return render_template('user_settings.html')

@app.route('/sessions', methods=['GET'])
def previous_sessions_view():
    return render_template('previous_sessions.html')

@app.route('/assets', methods=['GET', 'POST'])
def asset_management_view():
    return render_template('asset_management.html')

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    pass

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    return render_template('register.html')

@app.route('/compare_phrases', methods=['POST'])
def compare_phrases():

    recognised_tags = json.loads(request.form.get('recognisedTags'))
    mentioned_tags = request.form.get('mentionedTags')


    if not mentioned_tags:
        mentioned_tags = {'recent' : {},
                    'all' : {}
                }
    else:
        mentioned_tags = json.loads(mentioned_tags)

    # CREATE LIST OF ALL EXISTING TAGS ON ASSETS - THIS WOULD BE STORED OFC
    tag_pool = []
    for asset in assets:
        for tag in asset['tags']:
            if tag not in tag_pool:
                tag_pool.append(tag)

    sorting_obj = {'assetResults' : {'current' : [],
                                    'frequent' :[]},
                'mentionedTags' : {}
            }

    # UPDATE THE MENTIONED_TAGS OBJECT
    for word in recognised_tags:
        # IF THE WORD IS NOT IN THE TAGS, INITIALISE - SSEPARATELY FOR RECENT AND ALL
        all_tags = mentioned_tags.get('all')
        recent_tags = mentioned_tags.get('recent')
        if not all_tags.get(word):
            mentioned_tags['all'][word] = {'mentions' : 0}
            print("Initialised mentioned_tags['all']['" + word + "]")
        if not recent_tags.get(word):
            mentioned_tags['recent'][word] = {'mentions' : 0}
            print("Initialised mentioned_tags['recent']['" + word + "]")

        # ADD THE NEW TAG TO THE MENTIONED_TAGS OBJ
        mentioned_tags['all'][word]['mentions'] += 1
        mentioned_tags['recent'][word]['mentions'] += 1
        print("Adding mention to " + word + " in  RECENT")
    # recent_tags = sortingObj.get(mentionedTags).get('recent')
    # session['recent']
    # sesssion['frequent']

    sorting_obj['mentionedTags'] = mentioned_tags

    frequent_assets = []
    current_assets = []

    # MANAGE ADDING asset_selection
    for asset in assets:
        ###### FOR ALL -> FREQUENT
        mentioned_all = mentioned_tags['all'].keys()
        asset['weight'] = 0
        # LOOP FOR UPDATING WEIGHT
        for tag in mentioned_all:
            if tag in asset['tags']:
                asset['weight'] += mentioned_tags['all'][tag]['mentions']
        # LOOP TO ADD FOUND ONES, BREAK SO IT ONLY ADDS ASSET ONCE IF
        # IT HAS MORE THAN ONE MATCHING TAG
        for tag in mentioned_all:
            if tag in asset['tags']:
                frequent_assets.append(asset)
                break

        #CREATE A COPY OF THE ASSET SO THE FREQUENT_ASSETS IS NOT OVERRIDEN
        asset2 = copy.copy(asset)
        ###### FOR RECENT -> CURRENT
        mentioned_recent = mentioned_tags['recent'].keys()
        asset2['weight'] = 0
        # LOOP FOR UPDATING WEIGHT
        for tag in mentioned_recent:
            if tag in asset2['tags']:
                asset2['weight'] += mentioned_tags['recent'][tag]['mentions']

        # LOOP TO ADD FOUND ONES, BREAK SO IT ONLY ADDS ASSET ONCE IF
        # IT HAS MORE THAN ONE MATCHING TAG
        for tag in mentioned_recent:
            if tag in asset2['tags']:
                current_assets.append(asset2)
                break

    sorted_frequent =  sorted(frequent_assets, key=itemgetter('weight'), reverse=True)
    sorted_current = sorted(current_assets, key=itemgetter('weight'), reverse=True)
    sorting_obj['assetResults']['frequent'] = sorted_frequent
    sorting_obj['assetResults']['current'] = sorted_current

    return json.dumps(sorting_obj)
