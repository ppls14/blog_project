from flask import render_template, request, session, flash, redirect, url_for
from blog import app, forms
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm
import functools

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
                    post_content=form.post_content.data,
                    is_public=form.is_public.data
                )
                db.session.add(new_post)
                if new_post.is_public:
                    flash(f"Wpis o tytule {form.title.data} został opublikowany")
                else:
                    flash(f"Wpis o tytule {form.title.data} został zapisany do zakładki Niepubliczne wpisy")
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