from flask import Flask, render_template ,request,flash,session,redirect, url_for
from database import User,add_to_db,open_db, Upload
import os
from werkzeug.utils import secure_filename
import requests
import google.generativeai as genai
import os
import dotenv
dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = 'thisissupersecretkeyfornoone'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['HISTORY'] = []

os.makedirs('static/uploads',exist_ok=True)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]



def generate_caption(image_path):
    GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
    print(GOOGLE_API_KEY)
    genai.configure(api_key=GOOGLE_API_KEY)
    imageObj = genai.upload_file(path=image_path)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest",
                                  safety_settings=safety_settings)
    question = "generation only one caption for this image"
    response = model.generate_content([question, imageObj])
    ans = response.text
    app.config['HISTORY'].append(ans)
    return ans

def query_on_image(image_path, query):
    GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    imageObj = genai.upload_file(path=image_path)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest",
                                  safety_settings=safety_settings)
    response = model.generate_content([query, imageObj])
    app.config['HISTORY'].append(response.text)
    return response.text






@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password=request.form.get('password')
        if len(username) == 0 or len(password) == 0:
            flash('All fields are required','danger')
            return redirect('/login')
        db = open_db()
        user = db.query(User).filter(User.username==username).first()
        if user is None:
            flash('User not found','danger')
            return redirect('/login')
        if user.password != password:
            flash('Password is incorrect','danger')
            return redirect('/login')
        session['user_id'] = user.id
        session['isauth'] = True
        session['username'] = user.username
        flash('Logged in successfully','success')
        return redirect('/')
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method =='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        cpassword=request.form.get('cpassword')
        print(username,email,password,cpassword)
        db = open_db()
        if len(username) == 0  or len (email)== 0 or len(password)== 0 or len(cpassword) == 0:
            flash('All fields are required','danger')
            return redirect('/register')
        if password != cpassword:
            flash('Password and Confirm Password should be same','danger')
            return redirect('/register')
        if db.query(User).filter(User.email==email).first():
            flash('User already exists','danger')
            return redirect('/register')
        if db.query(User).filter(User.username==username).first():
            flash('Username already exists','danger')
            return redirect('/register')
        user=User(username=username,email=email,password=password)
        add_to_db(user)
        flash('User registered successfully','success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully','success')
    return redirect('/login')

@app.route('/upload',methods=['GET','POST'])
def upload():
    if not session.get('isauth'):
        flash('Login to upload file','danger')
        return redirect('/login')
    if request.method == 'POST':
        imagefile=request.files['image']
        if imagefile:
            if imagefile.filename == '':
                flash('No selected file','danger')
                return redirect('/upload')
            filename = secure_filename(imagefile.filename)
            imagefile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            title = ''
            description = ''
            user_id = session.get('user_id')
            upload = Upload(title=title, description=description, file_path=filename, user_id=user_id)
            add_to_db(upload)
            flash('File uploaded successfully','success')
            return redirect('/upload')
        else:
            flash('No file part','danger')
            return redirect('/uploads') 
    return render_template('upload.html')

@app.route('/uploads', methods=['GET','POST'])
def uploads():
    if not session.get('isauth'):
        flash('Login to view uploads','danger')
        return redirect('/login')
    user_id = session.get('user_id')
    db = open_db()
    uploads = db.query(Upload).filter(Upload.user_id==user_id).all()
    return render_template('uploads.html',uploads=uploads)

# chatbot
@app.route('/chat/<int:id>',methods=['GET','POST'])
def chatbot(id):
    db = open_db()
    image = db.query(Upload).filter(Upload.id==id).first()
    if request.method == 'POST':
        query=request.form.get('query')
        if query:
            response = query_on_image(os.path.join(app.config['UPLOAD_FOLDER'], image.file_path), query)
            image =db.query(Upload).filter(Upload.id==id).first()
            return render_template('chatbot.html',caption=response,image=image)
        else:
            flash('No query found','danger')
            return redirect('/chat/'+str(id))
    return render_template('chatbot.html',image=image)
            
        


@app.route('/query',methods=['GET','POST'])
def query():
    if request.method == 'POST':
        query=request.form.get('query')
        filename=request.form.get('filename')
        if query:
            response = query_on_image(os.path.join(app.config['UPLOAD_FOLDER'], filename), query)
            return render_template('chatbot.html',caption=response,filename=filename)
        else:
            flash('No query found','danger')
            return redirect('/query')
    return render_template('query.html')

@app.route('/history')
def history():
    return render_template('history.html',history=app.config['HISTORY'])


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True) 
 

