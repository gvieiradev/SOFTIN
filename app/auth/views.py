from flask import Flask, render_template, request, flash, redirect, url_for, session
from . import auth
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)

mysql = MySQL(cursorclass=DictCursor)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'haruko.17'
app.config['MYSQL_DATABASE_DB'] = 'residenciadb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@auth.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST" and 'users_name' in request.form and 'passw' in request.form:
        users_name = request.form['users_name']
        passw = request.form['passw']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE users_name=%s AND passw=%s', (users_name,passw))
        user = cursor.fetchone()
        
        if user:
            session['loggedin'] = True
            session['ci'] = user['ci_lessor']
            session['users_name'] = user['users_name']
            session['passw'] = user['passw']
            session['user_mail'] = user['user_mail']
            return redirect(url_for('auth.menu'))
        else:
            error_message = 'Usuario o contraseña invalidos!'
            flash(error_message)
    return render_template('login.html')

@auth.route('/Registrar', methods=["GET","POST"])
def create_account():
    if (request.method=="POST"):
        ci = request.form['ci']
        name = request.form['name']
        last_name = request.form['last_name']
        mail = request.form['email']
        phone = request.form['phone']
    
        sql = "INSERT INTO lessor (ci_lessor,first_name,last_name,mail,phone) VALUES ( %s,%s,%s,%s,%s)"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(ci,name,last_name,mail,phone))
        conn.commit()
    
        return redirect(url_for('auth.create_user'))
    else:        
        return render_template('create_account.html')

@auth.route('/Registrar_usuario', methods=["GET","POST"])
def create_user():
    if (request.method == "POST"):
        users_name = request.form['users_name']
        passw = request.form['passw']
        mail = request.form['mail']
        ci = request.form['ci'] #FOREIGN KEY 
        
        sql = "INSERT INTO user (users_name, passw, user_mail, ci_lessor) VALUES (%s, %s, %s, %s)"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(users_name,passw, mail, ci))
        conn.commit()
        
        return redirect(url_for('auth.login'))
    else:
        return render_template('create_user_account.html')

@auth.route('/menu')
def menu():
    return render_template('menu.html')

@auth.route('/usuarios')
def user():
    sql_user = "SELECT users_name, user_mail FROM user"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql_user)
    user = cursor.fetchall()
    conn.commit()
    return render_template('user.html', user=user)

@auth.route('/usuarios_editar', methods=['GET','POST'])
def user_edit():
    context={
        'ci':session['ci'],
        'user':session['users_name'],
        'mail':session['user_mail'],
        'pass':session['passw']
    }
    
    if request.method =='POST':
        ci = request.form['ci']
        users_name = request.form['users_name']
        user_mail = request.form['user_mail']
        passw = request.form['passw']
        
        sql = 'UPDATE user SET users_name=%s, user_mail=%s, passw=%s WHERE ci_lessor=%s'
        datos =  (users_name,user_mail,passw,ci)
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,datos)
        conn.commit()
        return redirect(url_for('auth.user'))
    return render_template('user_edit.html', **context)

@auth.route('/usuarios_eliminar')
def user_delete():
    sql = 'SELECT * FROM user'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    user=cursor.fetchall()
    conn.commit()
    return render_template('user_delete.html', user=user)

@auth.route('/destroy/<int:id_user>')
def destroy(id_user):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM user WHERE id_user=%s',(id_user))
    conn.commit()
    return redirect(url_for('auth.user'))

@auth.route('/muebles')
def furniture():
    sql = 'SELECT types, size, available FROM furniture'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    furniture = cursor.fetchall()
    conn.commit()
    return render_template('furniture.html', furniture=furniture)

@auth.route('/muebles_registrar', methods=['GET','POST'])
def furniture_register():
    if (request.method == 'POST'):
        types = request.form['types']
        size = request.form['size']
        available = request.form['available']
        
        sql = 'INSERT INTO furniture(types,size,available) VALUES (%s,%s,%s)'
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(types,size,available))
        conn.commit()
        
        return redirect(url_for('auth.furniture'))
    else:
        return render_template('furniture_register.html')

@auth.route('/muebles_modificar')
def furniture_modify():
    sql='SELECT * FROM furniture'
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    furniture=cursor.fetchall()
    conn.commit()
    return render_template('furniture_modify.html', furniture=furniture)

@auth.route('/editar/<int:id_furniture>')
def edit_furniture(id_furniture):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM furniture WHERE id_furniture=%s',(id_furniture))
    furniture=cursor.fetchall()
    conn.commit()
    return render_template('edit_furniture.html', furniture=furniture)

@auth.route('/update', methods=['POST'])
def update():
    types = request.form['types']
    size = request.form['size']
    available = request.form['available']
    id_furniture=request.form['id_furniture']
    
    sql='UPDATE furniture SET types=%s, size=%s, available=%s WHERE id_furniture=%s'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,(types,size,available,id_furniture))
    conn.commit()
    return redirect(url_for('auth.furniture'))

@auth.route('/muebles_eliminar')
def remove_furniture():
    sql = 'SELECT * FROM furniture'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    furniture=cursor.fetchall()
    conn.commit()
    return render_template('remove_furniture.html', furniture=furniture)

@auth.route('/muebles_destroy/<int:id_furniture>')
def muebles_destroy(id_furniture):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM furniture WHERE id_furniture=%s', (id_furniture))
    conn.commit()
    return redirect(url_for('auth.furniture'))

@auth.route('/residentes')
def resident():
    sql='SELECT * FROM lessee'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    lessee=cursor.fetchall()
    conn.commit()
    return render_template('resident.html',lessee=lessee)

@auth.route('/residentes_registrar', methods=['GET','POST'])
def resident_register():
    sql='SELECT * FROM furniture'
    conn= mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    furniture=cursor.fetchall()
    conn.commit()
    
    sql='SELECT * FROM lessor'
    conn= mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    lessor=cursor.fetchall()
    conn.commit()
    
    if (request.method == 'POST'):
        ci_lessee = request.form['ci']
        f_name = request.form['f_name']
        s_name = request.form['s_name']
        f_lastname = request.form['f_lastname']
        s_lastname = request.form['s_lastname']
        sex = request.form['sex']
        age = request.form['age']
        phone = request.form['phone']
        mail = request.form['mail']
        occupation = request.form['occupation']
        work = request.form['work']
        city = request.form['city']
        couple = request.form['couple']
        children = request.form['children']
        contracts = request.form['contracts']
        ci_lessor = request.form['ci_lessor']
        id_furniture = request.form['id_furniture']

        sql = 'INSERT INTO lessee(ci_lessee, f_name, s_name, f_lastname, s_lastname, sex, age, phone, mail, occupation, work, city, couple, children, contracts, ci_lessor, id_furniture) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,(ci_lessee, f_name, s_name, f_lastname, s_lastname, sex, age, phone, mail, occupation, work, city, couple, children, contracts, ci_lessor, id_furniture))
        conn.commit()
        
        return redirect(url_for('auth.resident'))
    else:
        return render_template('resident_register.html', furniture=furniture, lessor=lessor)

@auth.route('/residentes_modificar')
def resident_modify():
    sql='SELECT * FROM lessee'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    lessee=cursor.fetchall()
    conn.commit()
    return render_template('resident_modify.html',lessee=lessee)

@auth.route('/modificar/<int:ci_lessee>', methods=['GET','POST'])
def modify(ci_lessee):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM lessee WHERE ci_lessee=%s',(ci_lessee))
    lessee=cursor.fetchall()
    conn.commit()
    
    if (request.method == 'POST'):
        ci_lessee = request.form['ci']
        f_name = request.form['f_name']
        s_name = request.form['s_name']
        f_lastname = request.form['f_lastname']
        s_lastname = request.form['s_lastname']
        sex = request.form['sex']
        age = request.form['age']
        phone = request.form['phone']
        mail = request.form['mail']
        occupation = request.form['occupation']
        work = request.form['work']
        city = request.form['city']
        couple = request.form['couple']
        children = request.form['children']
        contracts = request.form['contracts']
        ci_lessor = request.form['ci_lessor']
        id_furniture = request.form['id_furniture']
    
        sql='UPDATE lessee SET f_name=%s, s_name=%s, f_lastname=%s, s_lastname=%s, sex=%s, age=%s, phone=%s, mail=%s, occupation=%s, work=%s, city=%s, couple=%s, children=%s, contracts=%s, ci_lessor=%s, id_furniture=%s WHERE ci_lessee=%s'
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,(ci_lessee, f_name, s_name, f_lastname, s_lastname, sex, age, phone, mail, occupation, work, city, couple, children, contracts, ci_lessor, id_furniture))
        conn.commit()
        return redirect(url_for('auth.resident'))
    else:
        return render_template('change_resident.html', lessee=lessee)

@auth.route('/residente_eliminar')
def lessee_delete():
    sql='SELECT * FROM lessee'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    lessee=cursor.fetchall()
    conn.commit()
    return render_template('lessee_delete.html', lessee=lessee)

@auth.route('/lessee_destroy/<int:ci_lessee>')
def lessee_destroy(ci_lessee):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lessee WHERE ci_lessee=%s',(ci_lessee))
    conn.commit()
    return redirect(url_for('auth.resident'))