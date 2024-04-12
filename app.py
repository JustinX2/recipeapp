from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from models import db, User, Recipe, connect_db
from forms import RegisterForm, LoginForm, RecipeForm
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flasklogin"
app.config['SECRET_KEY'] = 'abc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG'] = True

connect_db(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
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
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Failed. Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
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
        new_recipe = Recipe(
            title=form.title.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            image_url=form.image_url.data,
            user_id=current_user.id
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe successfully created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_recipe.html', form=form)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/recipe/<int:recipe_id>/update', methods=['GET', 'POST'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author.id != current_user.id:
        flash('You are not authorized to update this recipe.', 'danger')
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

@app.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author.id != current_user.id:
        flash('You are not authorized to delete this recipe.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully', 'success')
    return redirect(url_for('index'))

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

@app.errorhandler(Exception)
def handle_error(e):
    app.logger.error(f'An error occurred: {e}')
    return 'An internal server error occurred. Please try again later.', 500

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
