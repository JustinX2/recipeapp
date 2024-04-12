# [The Recipe App]

## Project Overview
The recipe app allows users to create, update, and delete recipes. The app also allows users to perform recipe search using TheMealDB API. 

## Project Features
1. **Create Recipe:** Users can create recipe including title, ingredients, instructions and an image URL
2. **Update and Delete Recipe:** Users can make updates to the recipes created. Users may also delete their recipes
3. **Search Recipe:** Users can search recipes from [TheMealDB API](https://www.themealdb.com/) and have their search results displayed
4. **User Profile:** Users can register their profile including username, email and password. This profile information is displayed on a profile page

## Webpage Flow
1. base.html: The base template provides Register and Login function. 
2. index.html: The homepage that displays the user's recipes, with options to create, update, and delete recipes. It also allows users to search for recipes from TheMealDB. There is also a link to the user profile page (profile.html)
3. register.html: The registration page where users can create a new account.
4. login.html: The login page where users can enter their email and password to log in.
5. profile.html: The user's profile page, displaying their username, password and email.
6. recipe_form.html: The page for creating a recipe, with fields for the title, description, ingredients, instructions, and image URL.
7. recipe_detail.html: The page that displays the details of a specific recipe, including the title, description, ingredients, and instructions. There is also option to edit or delete recipe.
8. recipe_list.html: The page that displays a list of all recipes.
9. user_recipe.html: The page that displays the user's own recipes, with options to add and edit them.
10. search.html: The page that allows users to search for recipes using the MealDB API.
11. search_results.html: The page that displays the results of a recipe search using the MealDB API.
