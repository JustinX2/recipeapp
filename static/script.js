document.addEventListener("DOMContentLoaded", function(){
    const loginForm=document.getElementById("login-form");
    if (loginForm){
        loginForm.addEventListener("submit", function(event){
            event.preventDefault();
            console.log("Login form submitted")
        });
    }

    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", function(event) {
            event.preventDefault(); 
            console.log("Register form submitted");
        });
    }

    const recipeForm = document.getElementById("recipe-form");
    if (recipeForm) {
        recipeForm.addEventListener("submit", function(event) {
            event.preventDefault(); 
            console.log("Recipe form submitted");
        });
    }

})
