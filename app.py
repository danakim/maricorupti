#!/usr/bin/python

from flask import Flask, render_template, request
from flaskext.mysql import MySQL
from datetime import date
import re
import ConfigParser

def create_app():
    # Initializing the app and Mysql connection
    mysql = MySQL()
    app = Flask(__name__)
    config = ConfigParser.ConfigParser()
    config.read('db.ini')
    app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'user')
    app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
    app.config['MYSQL_DATABASE_DB'] = config.get('mysql', 'database')
    app.config['MYSQL_DATABASE_HOST'] = config.get('mysql', 'host')

    mysql.init_app(app)
    cursor = mysql.connect().cursor()

    @app.route('/')
    def home_page():
        cursor.execute("SELECT MAX(data_condamnarii) from dosare_corupti")
        data_condamnarii = cursor.fetchone()
        today = date.today()
        ultima_condamnare = today - data_condamnarii[0]
        cursor.execute("SELECT COUNT(id) from dosare_corupti")
        total_dosare = cursor.fetchone()
        cursor.execute("SELECT COUNT(id) from dosare_corupti where executare=1")
        total_dosare_cu_executare = cursor.fetchone()
        cursor.execute("SELECT COUNT(id) from dosare_corupti where executare=0")
        total_dosare_fara_executare = cursor.fetchone()
        cursor.execute("SELECT MAX(ani_inchisoare) from dosare_corupti")
        pedeapsa_maxima = cursor.fetchone()
        cursor.execute("SELECT MAX(durata_dosar) from dosare_corupti")
        dosar_maxim = cursor.fetchone()

        # Send all the variables to the template
        return render_template(
            'index.html',
            ultima_condamnare=ultima_condamnare.days,
            total_dosare=total_dosare[0],
            total_dosare_cu_executare=total_dosare_cu_executare[0],
            total_dosare_fara_executare=total_dosare_fara_executare[0],
            pedeapsa_maxima=pedeapsa_maxima[0],
            dosar_maxim=dosar_maxim[0]
            )
        cursor.close ()

    @app.route('/dosare')
    def dosare():
        filtru = request.args.get('filtru')
        if filtru == 'cu_executare':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti where executare=1")
        elif filtru == 'fara_executare':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti where executare=0")
        elif filtru == 'nume':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by nume")
        elif filtru == 'functie_publica':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by functie_publica")
        elif filtru == 'partid':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by partid_1")
        elif filtru == 'fapta':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by fapta")
        elif filtru == 'data_sentinta':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by data_condamnarii")
        elif filtru == 'durata_dosar':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by durata_dosar")
        elif filtru == 'ani_pedeapsa':
            cursor.execute("SELECT id,nume,prenume,functie_publica,partid_1,fapta,ani_inchisoare,img_url from dosare_corupti order by ani_inchisoare")
        dosare = cursor.fetchall()

        # Send all the variables to the template
        return render_template(
            'dosare.html',
            dosare=dosare
            )
        cursor.close ()

    @app.route('/profil')
    def profil():
        return render_template(
            'profil.html'
            )

    @app.route('/despre')
    def despre():
        return render_template(
            'despre.html'
            )

    # Return the html
    return app

if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0')
