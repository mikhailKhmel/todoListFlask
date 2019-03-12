from flask import Flask, request, templating, render_template, redirect, session, url_for, abort
import sqlite3
import os

app = Flask(__name__)
current_user = ''
current_todolist = ''


def query(sql):
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result


@app.route('/')
def start():
    return render_template('login.html', check=True)


@app.route('/check_user', methods=['POST'])
def check_user():
    login = str(request.form['login'])
    password = str(request.form['password'])
    result = query('select Login, Password, todoList from Users')
    flag = False
    for user in result:
        if login == str(user[0]) and password == str(user[1]):
            flag = True
            global current_user
            global current_todolist
            current_user = login
            current_todolist = user[2]
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
        result = query('select * from Users')
        print(result)
        new_id = result[len(result) - 1][0] + 1
        new_todolist = 'todoList_' + login
        query('insert into Users (id, Login, Password, todoList) values (' + str(new_id) + ', "' + str(
            login) + '", "' + str(password) + '", "' + new_todolist + '")')
        query('CREATE TABLE "' + new_todolist + '" ("id" INTEGER, "done" INTEGER, "text" TEXT, "date" TEXT)')

        return redirect(url_for('start', check=True))


@app.route('/save_tasks', methods=['POST'])
def save_tasks():
    global current_user
    global current_todolist
    form_dict = request.form.to_dict()
    current_number_of_tasks = len(query('select * from ' + current_todolist))
    print(current_number_of_tasks)
    for i in range(1, current_number_of_tasks + 1):
        current_id = str(i)
        s_task = 'task' + str(i)
        s_date = 'date' + str(i)
        dones = form_dict.keys()
        flag = False
        for l in dones:
            if l == 'done' + str(i):
                flag = True
        current_task = str(form_dict.get(s_task))
        current_date = str(form_dict.get(s_date))
        if flag:
            qry = 'delete from ' + current_todolist + ' where id=' + current_id
            query(qry)
        else:
            qry = 'update ' + current_todolist + ' set done=0, text="' + current_task + '", date="' + current_date + '" where id=' + current_id
            query(qry)
    return redirect(url_for('hello_world', username=current_user))


@app.route('/<username>')
def hello_world(username):
    result = query('select * from Users')
    flag = False
    global current_user
    global current_todolist
    if current_user == '' or current_user != username:
        return redirect(url_for('start', check=True))
    for row in result:
        if row[1] == username:
            current_user = username
            current_todolist = row[3]
            flag = True
    if flag:
        user_list = query('select * from ' + current_todolist)
        return render_template('main.html', user_list=user_list)
    else:
        return redirect(url_for('new_user'))


@app.route('/new_task')
def new_task():
    return render_template('newtask.html')


@app.route('/add_newtask', methods=['POST'])
def add_newtask():
    global current_todolist
    result = query('select id from ' + current_todolist)
    new_id = len(result) + 1
    new_task = str(request.form['task'])
    new_date = str(request.form['date'])
    sql = 'insert into ' + current_todolist + ' (id,done,text,date) values (' + str(
        new_id) + ',0,"' + new_task + '","' + new_date + '");'
    query(sql)

    return redirect(url_for('hello_world', username=current_user))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
