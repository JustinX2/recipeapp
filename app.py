from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect
from models import db, User, Recipe, connect_db 
from forms import RegisterForm, LoginForm, RecipeForm
import requests
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123@localhost:5434/flasklogin"
app.config['SECRET_KEY'] = 'abc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


#context = app.app_context()
#context.push()
#db.create_all()

with app.app_context():
    connect_db(app)

 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

csrf = CSRFProtect(app)
toolbar = DebugToolbarExtension(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/index')
@login_required
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    #if request.method == 'POST':
        #print(request.form.get('username'))
    print('Form:', form)
    if form.validate_on_submit():
        print('hello')
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print('User:', user)
        flash('Registration Successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in Successfully', 'success')
            return redirect(url_for('index'))
        flash('Invalid email and password combination', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/recipe/create', methods=['GET', 'POST'])
@login_required
def create_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(
            title=form.title.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            image_url=form.image_url.data,
            author=current_user
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe successfully created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_recipe.html', form=form)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You are not authorized to update this recipe!', 'danger')
        return redirect(url_for('index'))
    
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.image_url = form.image_url.data
        db.session.commit()
        flash('Recipe successfully updated!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    return render_template('update_recipe.html', form=form, recipe=recipe)

@app.route('/recipe/<int:recipe_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You are not allowed to delete this recipe', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        db.session.delete(recipe)
        db.session.commit()
        flash('Recipe deleted successfully', 'success')
        return redirect(url_for('index'))
    return render_template('delete_recipe.html', recipe=recipe)

@app.route('/search', methods=['GET', 'POST'])
def search_recipes():
    if request.method == 'POST':
        search_query = request.form['search_query']
        url = f'https://www.themealdb.com/api/json/v1/1/search.php?s={search_query}'
        response = requests.get(url)
        data = response.json()
        meals = data.get('meals', [])
        return render_template('search_results.html', meals=meals)
    return render_template('search.html')

@app.route('/search_results')
def search_results():
    query = request.args.get('query', '')
    if query:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            meals = data.get('meals', [])
            return render_template('search_results.html', meals=meals, query=query)
        else:
            flash('Failed to find recipe', 'error')
            return redirect(url_for('search'))

@app.route('/database')
def load_database():
    with app.app_context():
        db.create_all()
    return 'Database created'

#if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
