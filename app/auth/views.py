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
    if request.method == "POST" and 'nombre_usuario' in request.form and 'clave' in request.form:
        nombre_usuario = request.form['nombre_usuario']
        clave = request.form['clave']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuario WHERE nombre_usuario=%s AND clave=%s', (nombre_usuario,clave))
        user = cursor.fetchone()
        
        if user:
            session['loggedin'] = True
            session['ci'] = user['ci_arrendador']
            session['nombre_usuario'] = user['nombre_usuario']
            session['clave'] = user['clave']
            session['correo'] = user['correo_usuario']
            return redirect(url_for('auth.menu'))
        else:
            error_message = 'Usuario o contraseña invalidos!'
            flash(error_message)
    return render_template('login.html')

@auth.route('/Registrar', methods=["GET","POST"])
def crear_cuenta():
    if (request.method=="POST"):
        ci = request.form['ci']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
    
        sql = "INSERT INTO arrendador (ci_arrendador,nombre,apellido,correo,telefono) VALUES ( %s,%s,%s,%s,%s)"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(ci,nombre,apellido,email,telefono))
        conn.commit()
    
        return redirect(url_for('auth.crear_usuario'))
    else:        
        return render_template('create_account.html')

@auth.route('/Registrar_usuario', methods=["GET","POST"])
def crear_usuario():
    if (request.method == "POST"):
        nombre_usuario = request.form['username']
        clave = request.form['clave']
        correo = request.form['correo_usuario']
        ci = request.form['ci'] #FOREIGN KEY 
        
        sql = "INSERT INTO usuario (nombre_usuario, clave, correo_usuario, ci_arrendador) VALUES (%s, %s, %s, %s)"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(nombre_usuario, clave, correo, ci))
        conn.commit()
        
        return redirect(url_for('auth.login'))
    else:
        return render_template('create_user_account.html')

@auth.route('/menu')
def menu():
    return render_template('menu.html')

@auth.route('/usuarios')
def usuarios():
    sql_user = "SELECT nombre_usuario, correo_usuario FROM usuario"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql_user)
    user = cursor.fetchall()
    conn.commit()
    return render_template('user.html', user=user)

@auth.route('/usuarios_editar', methods=['GET','POST'])
def usuarios_editar():
    context={
        'ci':session['ci'],
        'usuario':session['nombre_usuario'],
        'correo':session['correo'],
        'clave':session['clave']
    }
    
    if request.method =='POST':
        ci = request.form['ci']
        nombre_usuario = request.form['nombre_usuario']
        correo = request.form['correo']
        clave = request.form['clave']
        
        sql = 'UPDATE usuario SET nombre_usuario=%s, correo_usuario=%s, clave=%s WHERE ci_arrendador=%s'
        datos =  (nombre_usuario,correo,clave,ci)
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,datos)
        conn.commit()
        return redirect(url_for('auth.usuarios'))
    return render_template('user_edit.html', **context)

@auth.route('/usuarios_eliminar')
def usuarios_eliminar():
    sql = 'SELECT * FROM usuario'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    user=cursor.fetchall()
    conn.commit()
    return render_template('user_delete.html', user=user)

@auth.route('/destroy/<int:id_usuario>')
def destroy(id_usuario):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM usuario WHERE id_usuario=%s',(id_usuario))
    conn.commit()
    return redirect(url_for('auth.usuarios'))

@auth.route('/muebles')
def muebles():
    sql = 'SELECT tipo, tamanio, disponible FROM mueble'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    mueble = cursor.fetchall()
    conn.commit()
    return render_template('furniture.html', mueble=mueble)

@auth.route('/muebles_registrar', methods=['GET','POST'])
def muebles_registrar():
    if (request.method == 'POST'):
        tipo_mueble = request.form['tipo_mueble']
        tamanio_mueble = request.form['tamanio_mueble']
        disponibilidad = request.form['dispo']
        
        sql = 'INSERT INTO mueble(tipo,tamanio,disponible) VALUES (%s,%s,%s)'
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(tipo_mueble,tamanio_mueble,disponibilidad))
        conn.commit()
        
        return redirect(url_for('auth.muebles'))
    else:
        return render_template('furniture_register.html')

@auth.route('/muebles_modificar')
def muebles_modificar():
    sql='SELECT * FROM mueble'
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    mueble=cursor.fetchall()
    conn.commit()
    return render_template('furniture_modify.html', mueble=mueble)

@auth.route('/editar/<int:id_mueble>')
def editar(id_mueble):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM mueble WHERE id_mueble=%s',(id_mueble))
    mueble=cursor.fetchall()
    conn.commit()
    return render_template('edit_furniture.html', mueble=mueble)

@auth.route('/update', methods=['POST'])
def update():
    tipo_mueble = request.form['tipo_mueble']
    tamanio_mueble = request.form['tamanio_mueble']
    disponibilidad = request.form['dispo']
    id_mueble=request.form['id_mueble']
    
    sql='UPDATE mueble SET tipo=%s, tamanio=%s, disponible=%s WHERE id_mueble=%s'
    
    conn=mysql.connect()
    cursor=conn.cursor()
    
    cursor.execute(sql,(tipo_mueble,tamanio_mueble,disponibilidad,id_mueble))
    conn.commit()
    
    return redirect(url_for('auth.muebles'))

@auth.route('/muebles_eliminar')
def muebles_eliminar():
    sql = 'SELECT * FROM mueble'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    mueble=cursor.fetchall()
    conn.commit()
    return render_template('remove_furniture.html', mueble=mueble)

@auth.route('/muebles_destroy/<int:id_mueble>')
def muebles_destroy(id_mueble):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM mueble WHERE id_mueble=%s', (id_mueble))
    conn.commit()
    return redirect(url_for('auth.muebles'))

@auth.route('/residentes')
def residentes():
    sql='SELECT * FROM arrendatario'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    arrendatario=cursor.fetchall()
    conn.commit()
    return render_template('resident.html',arrendatario=arrendatario)

@auth.route('/residentes_registrar', methods=['GET','POST'])
def residentes_registrar():
    sql='SELECT * FROM mueble'
    conn= mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    mueble=cursor.fetchall()
    conn.commit()
    
    sql='SELECT * FROM arrendador'
    conn= mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    arrendador=cursor.fetchall()
    conn.commit()
    
    if (request.method == 'POST'):
        ci_arrendatario = request.form['ci']
        p_nombre = request.form['p_nombre']
        s_nombre = request.form['s_nombre']
        p_apellido = request.form['p_apellido']
        s_apellido = request.form['s_apellido']
        sexo = request.form['sexo']
        edad = request.form['edad']
        telefono = request.form['telefono']
        correo = request.form['correo']
        ocupacion = request.form['ocupacion']
        trabajo = request.form['trabajo']
        ciudad = request.form['ciudad']
        pareja = request.form['pareja']
        hijos = request.form['hijos']
        contrato = request.form['contrato']
        ci_arrendador = request.form['ci_arrendador']
        id_mueble = request.form['id_mueble']

        sql = 'INSERT INTO arrendatario(ci_arrendatario, p_nombre, s_nombre, p_apellido, s_apellido, sexo, edad, telefono, correo, ocupacion, trabajo, ciudad, pareja, hijos, contrato, ci_arrendador, id_mueble) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,(ci_arrendatario, p_nombre, s_nombre, p_apellido, s_apellido, sexo, edad, telefono, correo, ocupacion, trabajo, ciudad, pareja, hijos, contrato, ci_arrendador, id_mueble))
        conn.commit()
        
        return redirect(url_for('auth.residentes'))
    else:
        return render_template('resident_register.html', mueble=mueble, arrendador=arrendador)

@auth.route('/residentes_modificar')
def residentes_modificar():
    sql='SELECT * FROM arrendatario'
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    arrendatario=cursor.fetchall()
    conn.commit()
    return render_template('resident_modify.html',arrendatario=arrendatario)

@auth.route('/modificar/<int:ci_arrendatario>', methods=['GET','POST'])
def modifcar(ci_arrendatario):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM arrendatario WHERE ci_arrendatario=%s',(ci_arrendatario))
    arrendatario=cursor.fetchall()
    conn.commit()
    
    if (request.method == 'POST'):
        ci_arrendatario = request.form['ci']
        p_nombre = request.form['p_nombre']
        s_nombre = request.form['s_nombre']
        p_apellido = request.form['p_apellido']
        s_apellido = request.form['s_apellido']
        sexo = request.form['sexo']
        edad = request.form['edad']
        telefono = request.form['telefono']
        correo = request.form['correo']
        ocupacion = request.form['ocupacion']
        trabajo = request.form['trabajo']
        ciudad = request.form['ciudad']
        pareja = request.form['pareja']
        hijos = request.form['hijos']
        contrato = request.form['contrato']
        ci_arrendador = request.form['ci_arrendador']
        id_mueble = request.form['id_mueble']
    
        sql='UPDATE arrendatario SET p_nombre=%s, s_nombre=%s, p_apellido=%s, s_apellido=%s, sexo=%s, edad=%s, telefono=%s, correo=%s, ocupacion=%s, trabajo=%s, ciudad=%s, pareja=%s, hijos=%s, contrato=%s, ci_arrendador=%s, id_mueble=%s WHERE ci_arrendatario=%s'
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,(p_nombre, s_nombre, p_apellido, s_apellido, sexo, edad, telefono, correo, ocupacion, trabajo, ciudad, pareja, hijos, contrato, ci_arrendador, id_mueble, ci_arrendatario))
        conn.commit()
        return redirect(url_for('auth.residentes'))
    else:
        return render_template('change_resident.html', arrendatario=arrendatario)
