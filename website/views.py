from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Quote
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        theme = request.form.get('theme')#Gets theme from HTML 
        url = request.form.get('url')
        # print(theme)
        # print(url)

        quote = "Hello" # This is output

        if len(theme) < 1:
            flash('Theme is too short!', category='error') 
        elif len(url) < 5:
            flash('URL is too short!', category='error') 
        else:
            new_quote = Quote(data=quote, user_id=current_user.id)
            db.session.add(new_quote) #adding note to database 
            db.session.commit()
            flash('Note added!', category='success')
            pass

    return render_template("home.html", user=current_user)


@views.route('/delete-quote', methods=['POST'])
def delete_quote():  
    quote = json.loads(request.data)
    quoteId = quote['quoteId']
    quote = Quote.query.get(quoteId)
    if quote:
        if quote.user_id == current_user.id:
            db.session.delete(quote)
            db.session.commit()

    return jsonify({})