from flask import Flask, render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime # To add the date to the photo name
import os

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_BD']='workers'
mysql.init_app(app)

FOLDER= os.path.join('uploads')
app.config['FOLDER']=FOLDER

@app.route('/')
def index():
    sql = "SELECT * FROM `workers`.`workers`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    workers=cursor.fetchall()
    print(workers)
    conn.commit()
    return render_template('workers/index.html', workers=workers)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT photo FROM `workers`.`workers` WHERE id=%s",id)
    row= cursor.fetchall()
    os.remove(os.path.join(app.config['FOLDER'], row[0][0]))
    cursor.execute("DELETE FROM `workers`.`workers` WHERE id=%s", (id))
    conn.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `workers`.`workers` WHERE id=%s", (id))
    workers=cursor.fetchall()
    conn.commit()
    return render_template('workers/edit.html', workers=workers)

@app.route('/update', methods=['POST'])
def update():
    _name=request.form['txtName']
    _mail=request.form['txtMail']
    _photo=request.files['txtPhoto']
    id=request.form['txtID']
    sql = "UPDATE `workers`.`workers` SET `name`=%s, `mail`=%s WHERE id=%s;"
    data=(_name,_mail,id)
    conn = mysql.connect()
    cursor = conn.cursor()
    now= datetime.now()
    time= now.strftime("%Y%H%M%S")
    if _photo.filename!='':
        newPhotoname=time+_photo.filename
        _photo.save("uploads/"+newPhotoname)
        cursor.execute("SELECT photo FROM `workers`.`workers` WHERE id=%s", id)
        row= cursor.fetchall()
        os.remove(os.path.join(app.config['FOLDER'], row[0][0]))
        cursor.execute("UPDATE `workers`.`workers` SET photo=%s WHERE id=%s", (newPhotoname, id))
        conn.commit()
        return redirect('/')

    cursor.execute(sql,data)
    conn.commit()
    return redirect('/')

@app.route('/create')
def create():
    return render_template('workers/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _name=request.form['txtName']
    _mail=request.form['txtMail']
    _photo=request.files['txtPhoto']
    now= datetime.now()
    time= now.strftime("%Y%H%M%S")
    if _photo.filename!='':
        newPhotoName=time+_photo.filename
        _photo.save("uploads/"+newPhotoName)
    sql = "INSERT INTO `workers`.`workers` (`id`, `name`, `mail`, `photo`) VALUES (NULL, %s, %s, %s);"
    data=(_name,_mail,newPhotoName)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    # return render_template('workers/index.html')
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)