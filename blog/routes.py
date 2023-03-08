from flask import render_template, request, session, flash, redirect, url_for
from blog import app, forms
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm
import functools
from sqlalchemy import delete

def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
       if session.get('logged_in'):
           return view_func(*args, **kwargs)
       return redirect(url_for('login', next=request.path))
   return check_permissions

@app.route("/")
def index():
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())

   return render_template("homepage.html", all_posts=all_posts)

@app.route("/edit-post/<post_id>", methods = ["GET", "POST"]) 
@login_required
def edit_entry(post_id):
    post = Entry.query.filter_by(id=post_id).first()
    form = forms.EntryForm(obj=post)
    errors = None
    if request.method == "POST":
        if form.validate_on_submit():
            if post_id == 'new_id':
                new_post = Entry(
                    title=form.title.data,
                    body=form.body.data,
                    is_published=form.is_published.data
                )
                db.session.add(new_post)
                if new_post.is_published:
                    flash(f"Wpis o tytule {form.title.data} został opublikowany")
                else:
                    flash(f"Wpis o tytule {form.title.data} został zapisany do zakładki Szkice")
            elif post_id == str(post.id):
                form.populate_obj(post)
                flash(f"Wpis o tytule {form.title.data} został zmodyfikowany")
            db.session.commit()
        else:
            errors = form.errors
    return render_template("entry_form.html", form=form, errors=errors)

@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
       if form.validate_on_submit():
           session['logged_in'] = True
           session.permanent = True  # Use cookie to store session.
           flash('You are now logged in.', 'success')
           return redirect(next_url or url_for('index'))
       else:
           errors = form.errors
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'POST':
       session.clear()
       flash('You are now logged out.', 'success')
   return redirect(url_for('index'))

@app.route("/drafts/", methods=['GET'])
@login_required
def list_drafts():
   unpublic_posts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
   return render_template("drafts.html", all_posts=unpublic_posts)

@app.route("/delete-post/<post_id>", methods = [ "POST"])
@login_required
def delete_post(post_id):
    post = Entry.query.filter_by(id=post_id).first_or_404()
    form = forms.EntryForm(obj=post)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post: {form.title.data},został usunięty.", 'delete')
    return redirect(url_for('index'))