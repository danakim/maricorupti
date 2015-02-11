#!/usr/bin/python

from flask import Flask, render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import date
import re
import ConfigParser

# Initializing the app and Mysql connection
mysql = MySQL()
app = Flask(__name__)
## !! Turn debugging on - only for development !! ##
app.debug = True
##
# Read the config file for the mysql credentials
config = ConfigParser.ConfigParser()
config.read('db.ini')
app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'user')
app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DATABASE_DB'] = config.get('mysql', 'database')
app.config['MYSQL_DATABASE_HOST'] = config.get('mysql', 'host')

mysql.init_app(app)
cursor = mysql.connect().cursor()

# Landing page
@app.route('/')
def home_page():
    if request.args.get('filtru'):
        return redirect("/dosare?filtru=" + request.args.get('filtru'))
    else:
        cursor.execute("SELECT id, data_condamnarii FROM dosare_corupti ORDER BY data_condamnarii DESC limit 1")
        data_condamnarii = cursor.fetchall()
        today = date.today()
        ultima_condamnare = today - data_condamnarii[0][1]
        cursor.execute("SELECT COUNT(id) from dosare_corupti")
        total_dosare = cursor.fetchone()
        cursor.execute("SELECT COUNT(id) from dosare_corupti where executare=1")
        total_dosare_cu_executare = cursor.fetchone()
        cursor.execute("SELECT COUNT(id) from dosare_corupti where executare=0")
        total_dosare_fara_executare = cursor.fetchone()
        cursor.execute("SELECT id, ani_inchisoare FROM dosare_corupti ORDER BY ani_inchisoare DESC limit 1")
        pedeapsa_maxima = cursor.fetchall()
        cursor.execute("SELECT id, durata_dosar FROM dosare_corupti ORDER BY durata_dosar DESC limit 1")
        dosar_maxim = cursor.fetchall()

    # Send all the variables to the template
    return render_template(
        'index.html',
        ultima_condamnare=[data_condamnarii[0][0], ultima_condamnare.days],
        total_dosare=total_dosare[0],
        total_dosare_cu_executare=total_dosare_cu_executare[0],
        total_dosare_fara_executare=total_dosare_fara_executare[0],
        pedeapsa_maxima=pedeapsa_maxima[0],
        dosar_maxim=dosar_maxim[0]
        )

    cursor.close ()

# 'Dosare' page
@app.route('/dosare')
def dosare():
    filtru = request.args.get('filtru')
    if filtru == 'cu_executare':
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti where executare=1")
    elif filtru == 'fara_executare':
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti where executare=0")
    elif filtru in ['nume', 'functie_publica', 'partid_1', 'fapta', 'data_condamnarii', 'durata_dosar', 'ani_inchisoare']:
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti order by " + filtru)
    else:
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti WHERE (nume like '%" + filtru + "%' or prenume like '%" + filtru + "%' or functie_publica like '%" + filtru + "%' or partid_1 like '%" + filtru + "%' or fapta like '%" + filtru + "%') order by nume")
    dosare = cursor.fetchall()

    # Send all the variables to the template
    return render_template(
        'dosare.html',
        dosare=dosare
        )

    cursor.close ()

# 'Profile' page
@app.route('/profil')
def profil():
    id = request.args.get('id')
    cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,descriere_fapta,ani_inchisoare,img_url,executare,durata_dosar from dosare_corupti where id='" + id + "'")
    profil = cursor.fetchall()
    return render_template(
        'profil.html',
        profil=profil[0]
        )

# 'Despre' page
@app.route('/despre')
def despre():
    return render_template(
        'despre.html'
        )

# This is only used when running the app via
# flask's builtin webserver. We usually run this
# using uwsgi, so in theory no need for this
if __name__ == '__main__':
    app().run(debug=True, host='0.0.0.0')
