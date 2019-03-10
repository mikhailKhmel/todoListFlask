from flask import Flask, request, templating, render_template, redirect, session, url_for, abort
import sqlite3

app = Flask(__name__)
current_user = ''
current_todolist = ''
current_number_of_tasks = 0


def get_todolist(todo_list):
    db = sqlite3.connect('db.db')
    c = db.cursor()
    if c.execute('select * from ' + todo_list):
        result = c.fetchall()
        global current_number_of_tasks
        current_number_of_tasks = len(result)
        db.close()
        return result
    else:
        db.close()
        return 'Error'


@app.route('/')
def start():
    return render_template('login.html', check=True)


@app.route('/check_user', methods=['POST'])
def check_user():
    login = str(request.form['login'])
    password = str(request.form['password'])
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    sql = 'select Login, Password, todoList from Users'
    cur.execute(sql)
    result = cur.fetchall()
    flag = False
    print(login, '\t', password)
    for user in result:
        print(user[0], '\t', user[1])
        print(flag)
        if login == str(user[0]) and password == str(user[1]):
            flag = True
            global current_user
            global current_todolist
            current_user = login
            current_todolist = user[2]
    conn.close()
    if not flag:
        return render_template('login.html', check=False)
    else:
        return redirect(url_for('hello_world', username=current_user))


@app.route('/logout')
def logout():
    global current_user
    global current_todolist
    current_user = ''
    current_todolist = ''
    return redirect(url_for('start'))


@app.route('/newuser')
def new_user():
    return render_template('newuser.html')


@app.route('/addnewuser', methods=['POST'])
def add_newuser():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']
        db = sqlite3.connect('db.db')
        c = db.cursor()
        c.execute('select * from Users')
        result = c.fetchall()
        new_id = result[len(result) - 1][0] + 1
        new_todolist = 'todoList' + str(int(result[len(result) - 1][3][8:]) + 1)
        print(str(login) + '\t' + str(password) + '\t' + str(new_id) + '\t' + str(new_todolist))
        c.execute('insert into Users (id, Login, Password, todoList) values (?,?,?,?)',
                  [str(new_id), str(login), str(password), new_todolist])
        db.commit()
        c.execute('CREATE TABLE "' + new_todolist + '" ("done" INTEGER, "text" TEXT, "date" TEXT)')
        db.close()
        return 'added new user and created new todo list'


@app.route('/save_tasks', methods=['POST'])
def save_tasks():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    global current_user
    sql = 'SELECT todoList FROM Users WHERE Login="' + str(current_user) + '"'
    cursor.execute(sql)
    current_todolist_table = str(cursor.fetchone())[2:11]
    form_dict = request.form.to_dict()
    print('current_todolist_table=', current_todolist_table)
    global current_number_of_tasks
    for i in range(1, current_number_of_tasks + 1):
        s_task = 'task' + str(i)
        s_date = 'date' + str(i)
        dones = form_dict.keys()
        print(dones)
        flag = False
        for l in dones:
            print(l)
            if l == 'done' + str(i):
                flag = True
        current_task = form_dict.get(s_task)
        current_date = form_dict.get(s_date)

        if flag:
            qry = 'update ' + current_todolist_table + ' set done=1, text="' + current_task + '", date="' + current_date + '" where id=' + str(
                i) + '; '
        else:
            qry = 'update ' + current_todolist_table + ' set done=0, text="' + current_task + '", date="' + current_date + '" where id=' + str(
                i) + '; '

        conn.execute(qry)
        conn.commit()
    conn.close()
    return redirect(url_for('hello_world', username=current_user))


@app.route('/<username>')
def hello_world(username):
    db = sqlite3.connect('db.db')
    c = db.cursor()
    c.execute('select * from Users')
    result = c.fetchall()
    flag = False
    global current_user
    global current_todolist
    for row in result:
        if row[1] == username:
            global current_user
            global current_todolist
            current_user = username
            sql = 'SELECT todoList FROM Users WHERE Login="' + str(current_user) + '"'
            c.execute(sql)
            current_todolist = row[3]
            flag = True
    db.close()
    if flag:
        user_list = get_todolist(current_todolist)
        return render_template('main.html', user_list=user_list)
    else:
        return redirect(url_for('new_user'))


@app.route('/new_task')
def new_task():
    return render_template('newtask.html')


@app.route('/add_newtask', methods=['POST'])
def add_newtask():
    global current_todolist
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    sql = 'select id from ' + current_todolist
    cur.execute(sql)
    result = cur.fetchall()
    new_id = len(result) + 1
    print(request.form)
    new_task = str(request.form['task'])
    new_date = str(request.form['date'])
    sql = 'insert into ' + current_todolist + ' (id,done,text,date) values (' + str(
        new_id) + ',0,"' + new_task + '","' + new_date + '");'
    cur.execute(sql)
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world', username=current_user))


if __name__ == '__main__':
    app.run()
