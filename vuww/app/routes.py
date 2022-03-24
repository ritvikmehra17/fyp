from asyncio.windows_events import NULL
from flask import render_template,redirect,request,flash,session,url_for
from flask_login import logout_user,current_user, login_user, login_required
from app import app,db
from app.models import MySpot, User, MessageData, MyUpload, MyCube
from datetime import datetime
from werkzeug.utils import secure_filename
import os


@app.route('/home')
def home():
    return render_template('home.html',title='Home')


@app.route('/')
@app.route('/index')
@login_required
def index():
    imglist = MyCube.query.all()
    return render_template('index.html',title='Home', vrlist=imglist)

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Invalid username or password','danger')
                return redirect(url_for('login'))
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html', title='Sign In')

    
@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        email = request.form.get('email')
        username = request.form.get('username')
        cpassword = request.form.get('cpassword')
        password = request.form.get('password')
        # print(cpassword, password, cpassword==password)
        if username and password and cpassword and email:
            if cpassword != password:
                flash('Password do not match','danger')
                return redirect('/register')
            else:
                if User.query.filter_by(email=email).first() is not None:
                    flash('Please use a different email address','danger')
                    return redirect('/register')
                elif User.query.filter_by(username=username).first() is not None:
                    flash('Please use a different username','danger')
                    return redirect('/register')
                else:
                    user = User(username=username, email=email)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    flash('Congratulations, you are now a registered user!','success')
                    return redirect(url_for('login'))
        else:
            flash('Fill all the fields','danger')
            return redirect('/register')

    return render_template('register.html', title='Sign Up page')


@app.route('/forgot',methods=['GET', 'POST'])
def forgot():
    if request.method=='POST':
        email = request.form.get('email')
        if email:
            pass
    return render_template('forgot.html', title='Password reset page')
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user, title=f'{user.username} profile')


@app.before_request
def before_request():
    try:
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
    except:
        pass

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method=='POST':
        current_user.username = request.form.get('username')
        current_user.about_me = request.form.get('aboutme')
        db.session.commit()
        flash('Your changes have been saved.','success')
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', title='Edit Profile',user=user)


@app.route('/input',methods=['GET','POST'])
def input_page():
    if request.method =='POST':
        msg = request.form.get('msg')
        if msg: # not none
            if len(msg) >= 10: # just some validation
                msgObj = MessageData(message=msg)   # add data to model object
                db.session.add(msgObj)              # save data in database
                db.session.commit()                 # update database
                # prediction logic
                flash('we have saved ur data, prediction result will be available shortly','success')
            else:
                flash('message smaller than 10 characters cannot be predicted','danger')
        else:
            flash('message not provided, please fill in some data to predict')
    return render_template('input.html',title="Input data")


def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['GET','POST'])
def uploadImage():
    imglist = MyUpload.query.filter_by(user_id=current_user.id) 

    if request.method == 'POST':
        if 'file[]' not in request.files:
            flash('No file uploaded','danger')
            return redirect(request.url)
        files = request.files.getlist('file[]')
        print(type(files),files)
        for file in files:
            print(file)
            if file == '':
                flash('no file selected','danger')
               
            if file and allowed_files(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename ))
                upload = MyUpload(img =f"/static/uploads/{filename}", imgtype = os.path.splitext(file.filename)[1],user_id=current_user.id)
                db.session.add(upload)
                db.session.commit()
                flash('file uploaded and saved','success')
                session['uploaded_file'] = f"/static/uploads/{filename}"
                
            else:
                flash('wrong file selected, only PNG and JPG images allowed','danger')
        return redirect(request.url)
   
    return render_template('upload.html',title='upload new Image',imglist=imglist)



def clean_image_entries(imglist):
    for img in imglist:
        if not os.path.exists("app"+img.img):
            MyUpload.query.filter_by(id=img.id).delete()
            print('deleted',img.img)
    db.session.commit()



@app.route('/dashboard', methods=['GET','POST'])
def dashboardImage():
    imglist = MyUpload.query.filter_by(user_id=current_user.id)    
    clean_image_entries(imglist)
        
    return render_template('dashboard.html',title='Dashboard',imglist=imglist)

g=0
@app.route('/cube', methods=['GET','POST'])
def cubicImage():
    imglist = MyUpload.query.filter_by(user_id=current_user.id)
    if request.method == 'POST':
        data=request.form.to_dict(flat=True)
        images=(data.get('front'),data.get('back'),data.get('left'),data.get('right'),data.get('ceiling'),data.get('floor'))
        images_set = set(images)
        print(images)
        if len(images_set)==6 and  data.get('title'):
            c = MyCube(
                        front=images[0],
                        back=images[1],
                        left=images[2],
                        right=images[3],
                        ceiling=images[4],
                        floor=images[5],
                        user_id=current_user.id,
                        title=data.get('title'),
                        description=data.get('description'),
                        publish=True if data.get('publish') == 'true' else False
                        )
            
            db.session.add(c)
            db.session.commit()
            session['last_cube_id']=c.id
            flash('VR room generated and ready','success')
            # return redirect('/')         
            return redirect('/spot')    
        else:
            flash('All walls should be unique','danger')   

    return render_template('cube.html',title='Cubic Image',imglist=imglist)



@app.route('/spot', methods=['GET','POST'])
def spot_pos():   
    if session.get('last_cube_id'):
        if request.method == 'POST':
            data=request.form.to_dict(flat=True)
            c = MySpot(
                        x=data.get('x'),
                        y=data.get('y'),
                        z=data.get('z'),
                        cube_id=session.get('last_cube_id')
                        )
                    
            db.session.add(c)
            db.session.commit()
            flash('info spot generated','success')
            return redirect('/')         

        return render_template('spot.html',title="InfoSpot")
    else:
        flash("create a cube vr content first",'danger')
        return redirect('/cube')




@app.route('/remove/<int:id>',methods=['GET','POST'])
def removeImage(id):
    image = MyUpload.query.get(id)
    try:
        if os.path.exists('app'+image.img):
            os.unlink('app'+image.img)
        MyUpload.query.filter_by(id=id).delete()
        MyCube.query.filter_by(id=id).delete()
        db.session.commit()
        flash('image deleted successfully','success')
    except Exception as e:
        print(e)
        flash('houston we have a problem','danger')

    return redirect('/dashboard')


def remove_file(filename):
    try:
        if os.path.exists('app'+filename):
            os.unlink('app'+filename)
        else:
            print('file not found',filename)
    except Exception as e:
        print(e)


@app.route('/remove_vt/<int:id>',methods=['GET','POST'])
def removeVT(id):
    image = MyCube.query.get(id)
    print(type(image))
    try:
        remove_file(image.ceiling)
        remove_file(image.floor)
        remove_file(image.front)
        remove_file(image.back)
        remove_file(image.left)
        remove_file(image.right)
        MyUpload.query.filter_by(img=image.front).delete()
        MyUpload.query.filter_by(img=image.back).delete()
        MyUpload.query.filter_by(img=image.left).delete()
        MyUpload.query.filter_by(img=image.right).delete()
        MyUpload.query.filter_by(img=image.ceiling).delete()
        MyUpload.query.filter_by(img=image.floor).delete()
        MyCube.query.filter_by(id=id).delete()
        db.session.commit()
        flash('image deleted successfully','success')
    except Exception as e:
        print(e)
        flash(f'houston we have a problem {e}','danger')

    return redirect('/index')



@app.route('/vt/<int:id>',methods=['GET','POST'])
def virtualtour(id):
    vr = MyCube.query.get(id)
    spots = MySpot.query.filter_by(cube_id=session.get('last_cube_id'))
    for sp in spots:
        spx=sp.x
        spy=sp.y
        spz=sp.z
    title=(vr.title).replace(' ','_')
    loc = f"app/static/output/{title}/"
    os.mkdir(loc) if not os.path.exists(loc) else print('path found')
    save_path = os.path.join(loc,'cube')
    print(loc)
    print(save_path)
    for file in os.listdir(loc):
        if 'cube' in file:
            print('file exists no need to create')
            break
    else:
        cmd = f"cube2sphere {'app'+vr.front} {'app'+vr.back} {'app'+vr.left} {'app'+vr.right} {'app'+vr.ceiling} {'app'+vr.floor} -r 2048 1024 -fJPG -o{save_path}"
        stream = os.popen(cmd)
        out = stream.read()
        print(cmd)
        print(out)    
    save_path +="0001.png"
    save_path = save_path[3:]
    return render_template('vt.html',title='Virtual Tour',vr=vr,cube=save_path, info=vr.description,spx=spx,spy=spy,spz=spz)
    