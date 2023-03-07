from flask import render_template, request, flash
from blog import app, forms
from blog.models import Entry, db
from blog.forms import EntryForm

@app.route("/")
def index():
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())

   return render_template("homepage.html", all_posts=all_posts)

@app.route("/edit-post/<post_id>", methods = ["GET", "POST"]) 
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