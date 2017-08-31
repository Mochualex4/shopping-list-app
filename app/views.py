"""
Code for rendering the views
"""
from functools import wraps
from flask import request, session, redirect, url_for, render_template, flash

from app import app, user_object, list_object, item_object

def login_required(f):
    """
    Checks if a user is logged in
    """
    @wraps(f)
    def verified(*args, **kwargs):
        """
        Decorated function to check log in status
        """
        if "username" in session:
            return f(*args, **kwargs)
        else:
            msg = "You need to be logged in"
            return render_template("index.html", error=msg)
    return verified

@app.route('/')
def index():
    """
    Render the index page
    """
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register():
    """
    Register a user
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['conf_password']

        status = user_object.register(username, password, cpassword)
        if status == "Registered successfully":
            session['username'] = username
            return render_template('index.html', error=status)
        else:
            return render_template('index.html', resp=status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs in user and renders the user dashboard
    """
    if request.method == 'POST':
        username = request.form['username2']
        password = request.form['password2']

        status = user_object.login(username, password)
        if status == "Login successful":
            session['username'] = username

            return render_template('dashboard.html')
        else:
            return render_template('index.html', resp=status)

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Logs in user and renders the user dashboard
    """
    user = session['username']
    
    user_lists = list_object.show_lists(user)

    return render_template('dashboard.html', shopping_lists=user_lists)

@app.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
    """
    View used to create new shopping lists
    """
    user = session['username']

    if request.method == 'POST':
        list_name = request.form['name']
        description = request.form['description']
        status = list_object.create_list(user, list_name, description)

        if isinstance(status, list):
            user_lists = list_object.show_lists(user)
            return render_template('dashboard.html', shopping_lists=user_lists)
        else:
            return render_template("create_shopping_list.html", error=status)

    return render_template("create_shopping_list.html")

@app.route('/edit_list/<name>', methods=['GET', 'POST'])
@login_required
def edit_list(name):
    """
    View used to edit shopping lists
    """
    user = session['username']
    user_lists = list_object.show_lists(user)

    if request.method == 'POST':
        old_name = name
        new_name = request.form['name']
        description = request.form['description']
        status = list_object.update_list(old_name, new_name, description, user)

        if status == list_object.shopping_list:
            response = "" + name + " shopping list successfully updated"
            return render_template('dashboard.html', error=response, shoppinglist=status)
        else:
            return render_template('dashboard.html', error=status, shoppinglist=user_lists)
    
    return render_template("edit_shopping_list.html")

@app.route('/delete_list/<name>', methods=['POST'])
@login_required
def delete_list(name):
    """
    Used to delete shopping list
    """
    user = session['username']
    if request.method == 'POST':
        status = list_object.delete_list(name, user)
        # Delete list items
        item_object.delete_list_items(name)
        response = "Successfuly deleted " + name + " shopping list"
    
    return render_template("dashboard.html", error=response, shopping_lists=status)

@app.route('/view_list/<name>', methods=['GET'])
@login_required
def view_list(name):
    """
    View for displaying a particular shopping list and all its items
    """
    user = session['username']
    user_items = item_object.show_items(user, name)
    # Get all items belonging to a particular list through list comprehension
    list_items = [item['name'] for item in user_items if item['list'] == name]

    return render_template("shopping_list.html", list_name=name, item_list=list_items)

@app.route('/add_item/<list_name>', methods=['POST'])
@login_required
def add_item(list_name):
    """
    Add items to a list
    """
    user = session['username']

    if request.method == 'POST':
        item_name = request.form['name']
        status = item_object.add_item(user, list_name, item_name)
        if isinstance(status, list):
            return view_list(list_name)

@app.route('/edit_item/<list_name>/<item_name>', methods=['GET', 'POST'])
@login_required
def edit_item(list_name, item_name):
    """
    View for editing shopping list items
    """
    user = session['username']
    if request.method == 'POST':
        old_name = item_name
        new_name = request.form['name']

        status = item_object.update_item(old_name, new_name, list_name, user)
        if isinstance(status, list):
            response = "" + old_name + " successfully edited"
            # Get edited list of the current shopping list
            new_list = [item['name'] for item in status if item['list'] == list_name]
            return render_template("shopping_list.html", item_list=new_list, list_name=list_name, error=response)
        else:
            # Get user's items in the current shopping list
            user_items = item_object.show_items(user, list_name)
            new_list = [item['name'] for item in user_items if item['list'] == list_name]
            return render_template("shopping_list.html", item_list=new_list, list_name=list_name, error=status)

    return render_template("shopping_list_items_edit.html", list_name=list_name, item_name=item_name)

@app.route('/delete_item/<list_name>/<item_name>', methods=['POST'])
@login_required
def delete_item(list_name, item_name):
    """
    Used for deleting shopping list items
    """
    user = session['username']

    if request.method == 'POST':
        status = item_object.delete_item(item_name, user, list_name)
        response = "" + item_name +" successfuly deleted"

        if isinstance(status, list):
            list_items = [item['name'] for item in status if item['list'] == list_name]
            return render_template("shopping_list.html", list_name=list_name, item_list=status, item_name=item_name, error=response)
        else:
            user_items = item_object.show_items(user, list_name)
            list_items = [item['name'] for item in user_items if item['list'] == list_name]
            return render_template("shopping_list.html", list_name=list_name, item_list=list_items, item_name=item_name, error=response)

@app.route('/logout')
def logout():
    """
    Log out a user
    """
    session.pop('username', None)
    msg = "You were logged out"
    return render_template("index.html", error=msg)
