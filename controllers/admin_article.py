#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = ''' 
            SELECT 
                id_meuble AS id_article, type_meuble_id, libelle_type AS libelle, materiau_id,
                nom_meuble AS nom, stock, largeur, hauteur, 
                prix_meuble AS prix, fournisseur, marque, image_meuble as image
            FROM meuble
            INNER JOIN type_meuble ON type_meuble.id_type = meuble.type_meuble_id
            ORDER BY nom; '''
    mycursor.execute(sql)
    meubles = mycursor.fetchall()
    print(meubles)
    return render_template('admin/article/show_article.html', meubles=meubles)


@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()

    sql = '''
            SELECT
                id_type AS id_type_meuble,
                libelle_type as libelle
            FROM type_meuble; '''
    mycursor.execute(sql)
    type_article = mycursor.fetchall()

    return render_template('admin/article/add_article.html'
                           ,types_article=type_article,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    stock = request.form.get('stock', '')
    image = request.files.get('image', '')
    

    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.jpg'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    sql = '''  INSERT INTO meuble(nom_meuble,prix_meuble, stock, image_meuble, type_meuble_id, description, materiau_id)
                VALUES (%s, %s, %s, %s, %s, %s, 1); '''

    tuple_add = (nom, prix, stock, filename, type_article_id, description)
    print(tuple_add)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'article ajouté , nom: ', nom, ' - type_article:', type_article_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'article ajouté , nom:' + nom + '- type_article:' + type_article_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()

    #Suppresion d'un meuble    
    # sql = ''' SELECT * FROM declinaison WHERE meuble_id = %s; ''' # A décommenter une fois que la table declinaison aura été créee
    # mycursor.execute(sql, id_article)
    # nb_declinaison = mycursor.fetchone()
    nb_declinaison = {'nb_declinaison' : 0} # A enlever une fois que la table declinaison aura été créee
    if nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet article : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' SELECT * FROM meuble WHERE id_meuble = %s;  '''
        mycursor.execute(sql, id_article)
        meuble = mycursor.fetchone()
        print(meuble)
        image = meuble['image_meuble']

        sql = ''' DELETE FROM meuble WHERE id_meuble = %s;  '''
        mycursor.execute(sql, id_article)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un meuble supprimé, id :", id_article)
        message = u'un meuble supprimé, id : ' + id_article
        flash(message, 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''
            SELECT 
                id_meuble, type_meuble_id, nom_meuble AS nom, description, 
                stock, prix_meuble AS prix, image_meuble as image
            FROM meuble
            WHERE id_meuble = %s; '''
    mycursor.execute(sql, id_article)
    meuble = mycursor.fetchone()
    print(meuble)

    sql = '''
            SELECT
                id_type AS id_type_meuble,
                libelle_type as libelle
            FROM type_meuble; '''
    mycursor.execute(sql)
    types_meuble = mycursor.fetchall()

    # sql = '''
    # requête admin_article_6
    # '''
    # mycursor.execute(sql, id_article)
    # declinaisons_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html'
                           ,meuble=meuble
                           ,types_meuble=types_meuble
                         #  ,declinaisons_article=declinaisons_article
                           )


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')
    stock = request.form.get('stock', '')


    sql = '''
            SELECT image_meuble AS image FROM meuble WHERE id_meuble = %s;'''
    mycursor.execute(sql, id_article)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    sql = '''  
            UPDATE meuble SET 
                nom_meuble = %s, image_meuble = %s, prix_meuble = %s, 
                type_meuble_id = %s, description = %s, stock = %s WHERE id_meuble = %s; '''
    mycursor.execute(sql, (nom, image_nom, prix, type_article_id, description, stock, id_article))
    get_db().commit()

    if image_nom is None:
        image_nom = ''
    message = u'meuble modifié , nom:' + nom + '- type_article :' + type_article_id + ' - prix:' + prix  + ' - image:' + image_nom + ' - description: ' + description + 'stock:' + stock
    flash(message, 'alert-success')
    return redirect('/admin/article/show')


#Gestion des avis laisser par un utilisateur sur un produit
@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article=[]
    commentaires = {}
    return render_template('admin/article/show_avis.html'
                           , article=article
                           , commentaires=commentaires
                           )


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)

    return admin_avis(article_id)
