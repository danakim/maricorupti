#!/usr/bin/python

from flask import Flask, render_template, request, redirect
from datetime import date
import re
import ConfigParser
import mysql.connector
# This crap is needed to enforce utf-8 everywhere
# http://stackoverflow.com/questions/5040532/python-ascii-codec-cant-decode-byte
import sys
from collections import defaultdict
reload(sys)
sys.setdefaultencoding('utf-8')

# Initialize the app
app = Flask(__name__)
## !! Turn debugging on - only for development !! ##
app.debug = True
##

# Read the config file for the mysql credentials
config = ConfigParser.ConfigParser()
config.read('db.ini')

# Configure the mysql connection
db_config = {
  'user': config.get('mysql', 'user'),
  'password': config.get('mysql', 'password'),
  'unix_socket': config.get('mysql', 'socket'),
  'database': config.get('mysql', 'database'),
  'connection_timeout': float(config.get('mysql', 'conn_timeout')),
  'pool_size': float(config.get('mysql', 'conn_pool_size')),
}
cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

# Landing page
@app.route('/')
def home_page():
    # Always try and reconnect to Mysql,
    # the connection timeout may be expired
    cnx.reconnect(attempts=3, delay=1)

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
        cursor.execute("SELECT id, img_url_slider FROM dosare_corupti WHERE img_url_slider LIKE '%img%' ORDER BY RAND() LIMIT 1;")
        info_slider = cursor.fetchall()

    # Send all the variables to the template
    return render_template(
        'index.html',
        ultima_condamnare=[data_condamnarii[0][0], ultima_condamnare.days],
        total_dosare=total_dosare[0],
        total_dosare_cu_executare=total_dosare_cu_executare[0],
        total_dosare_fara_executare=total_dosare_fara_executare[0],
        pedeapsa_maxima=pedeapsa_maxima[0],
        dosar_maxim=dosar_maxim[0],
        info_slider=info_slider
        )

    cursor.close()

# 'Dosare' page
@app.route('/dosare')
def dosare():
    # Always try and reconnect to Mysql,
    # the connection timeout may be expired
    cnx.reconnect(attempts=3, delay=1)

    filtru = request.args.get('filtru').lower()
    if filtru == 'cu_executare':
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti where executare=1")
    elif filtru == 'fara_executare':
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti where executare=0")
    elif filtru in ['nume', 'functie_publica', 'partid_1', 'fapta', 'data_condamnarii', 'durata_dosar', 'ani_inchisoare']:
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti order by " + filtru)
    else:
        cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url,executare from dosare_corupti WHERE (LOWER(nume) like %(filtru)s or LOWER(prenume) like %(filtru)s or LOWER(functie_publica) like %(filtru)s or LOWER(partid_1) like %(filtru)s or LOWER(fapta) like %(filtru)s) order by nume", {'filtru': '%' + filtru + '%'})
    dosare = cursor.fetchall()

    # Send all the variables to the template
    return render_template(
        'dosare.html',
        dosare=dosare
        )

    cursor.close()

# 'Profile' page
@app.route('/profil')
def profil():
    # Always try and reconnect to Mysql,
    # the connection timeout may be expired
    cnx.reconnect(attempts=3, delay=1)

    id = request.args.get('id')
    cursor.execute("SELECT id, data_condamnarii FROM dosare_corupti WHERE NOT data_condamnarii = '0000-00-00' AND id='" + id + "'limit 1;")
    data_condamnarii = cursor.fetchall()
    cursor.execute("SELECT id, ani_inchisoare FROM dosare_corupti WHERE id='" + id + "'limit 1;")
    zile_inchisoare = cursor.fetchall()
    zile_inchisoare = int(zile_inchisoare[0][1]) * 365
    today = date.today()
    timp_condamnare = today - data_condamnarii[0][1]
    zile_ramase = zile_inchisoare - timp_condamnare.days
    cursor.execute("SELECT * from dosare_corupti where id='" + id + "'")
    profil = cursor.fetchall()
    return render_template(
        'profil.html',
        profil=profil[0],
        zile_ramase=zile_ramase,
        timp_condamnare=timp_condamnare.days
        )

    cursor.close()

# 'Despre' page
@app.route('/despre')
def despre():
    # Always try and reconnect to Mysql,
    # the connection timeout may be expired
    cnx.reconnect(attempts=3, delay=1)

    return render_template(
        'despre.html'
        )

@app.route('/statistici')
def statistici():
    # Always try and reconnect to Mysql,
    # the connection timeout may be expired
    cnx.reconnect(attempts=3, delay=1)

    # First chart data
    cursor.execute("SELECT * from dosare_corupti")
    dosare = [dict(zip(cursor.column_names, r)) for r in cursor.fetchall()]
    culoare_default = 'gray'
    culoare = {
        'PSD': 'color: red',
        'PNL': 'yellow',
        'PDL': 'orange',
        'UDMR': 'green',
        'PC': 'blue',
        'PNTCD': 'green',
        'PP-DD': '#C292E1'
    }
    partide_count = defaultdict(int)
    for d in dosare:
        partide_count[d['partid_1'] or 'N/A'] += 1
    partide = [(k, partide_count[k], culoare.get(k, culoare_default)) for k in partide_count]
    partide.sort(key=lambda p: p[1], reverse=True)

    # Second chart data
    cursor.execute("SELECT COUNT(id) from dosare_corupti where executare=1")
    total_dosare_cu_executare = cursor.fetchone()
    cursor.execute("SELECT COUNT(id) from dosare_corupti where executare=0")
    total_dosare_fara_executare = cursor.fetchone()

    # Data boxes
    cursor.execute("SELECT id, ani_inchisoare FROM dosare_corupti ORDER BY ani_inchisoare DESC limit 1")
    pedeapsa_maxima = cursor.fetchall()
    cursor.execute("SELECT id, durata_dosar FROM dosare_corupti ORDER BY durata_dosar DESC limit 1")
    dosar_maxim = cursor.fetchall()
    cursor.execute("SELECT id, durata_dosar FROM dosare_corupti WHERE NOT durata_dosar = 0 ORDER BY durata_dosar ASC limit 1")
    dosar_minim = cursor.fetchall()
    cursor.execute("SELECT count(distinct fapta), fapta FROM dosare_corupti")
    fapta_des = cursor.fetchall()
    total_condamnati = len(dosare)
    ani_executare = 0
    ani_suspendare = 0
    for d in dosare:
        if d['executare'] == 1:
            ani_executare = ani_executare + d['ani_inchisoare']
        else:
            ani_suspendare = ani_suspendare + d['ani_inchisoare']

    # Send it all to the template
    return render_template(
        'statistici.html',
        dosare=dosare,
        partide=partide,
        total_condamnati=total_condamnati,
        ani_executare=ani_executare,
        ani_suspendare=ani_suspendare,
        pedeapsa_maxima=pedeapsa_maxima[0],
        dosar_maxim=dosar_maxim[0],
        dosar_minim=dosar_minim[0],
        fapta_des=fapta_des[0],
        total_dosare_cu_executare=total_dosare_cu_executare[0],
        total_dosare_fara_executare=total_dosare_fara_executare[0],
        )


# This is only used when running the app via
# flask's builtin webserver. We usually run this
# using uwsgi, so in theory no need for this
if __name__ == '__main__':
    app().run(debug=True, host='0.0.0.0')
    cnx.close()
