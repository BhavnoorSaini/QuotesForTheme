from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Quote
from . import db
import json
from . import QuoteMatcher

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        theme = request.form.get('theme') # Get theme from HTML 
        url = request.form.get('url') # Get url from HTML

        # Calls and initalizes QuoteMatcherClass
        quote_matcher = QuoteMatcher.QuoteMatcherClass(url, theme)
        # Runs the quote search algorithm from class and stores quote that best supports theme
        matched_quote = quote_matcher.run()

        # If there is a quote that matches the theme, then output it to the program
        if matched_quote is not None:
            quote = matched_quote
        else:
            # Else output this statement to the program
            quote = "No quotes found."

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