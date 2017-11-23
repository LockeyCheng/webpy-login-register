#coding=utf-8
import sys,hashlib
reload(sys)
sys.setdefaultencoding('utf8')
import web
web.config.debug = False
from web import form
db = web.database(dbn='postgres', user='postgres', pw='redhat', db='lockey')
render = web.template.render('templates/')

urls = (
  '/', 'index',
  '/register','register',
  '/login', 'login',
  '/logout','logout'
)
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'username': None})
myform = form.Form( 
    form.Textbox("用户名",
        form.notnull,
        form.regexp('[A-Za-z0-9\-]+', 'Must be alpha or digit!'),
        form.Validator('Must be more than 5 characters!', lambda y:len(y)>5)), 
    form.Textbox("姓名", 
        form.notnull,
        form.regexp('\d+', 'Must be a digit'),
        form.Validator('Must be more than 5', lambda x:int(x)>5)),
    form.Password('密码'),
    form.Password('密码确认'))


class index: 
    def GET(self): 
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        if not session.username:
            raise web.seeother('/login')
        else:
            username = session.username
            return render.index(username)

loginform = form.Form(
    form.Textbox('username',
        form.notnull,
        form.regexp('[A-Za-z0-9\-]+', 'Must be alpha or digit!'),
        form.Validator('Must be more than 5 characters!', lambda y:len(y)>5)),
    form.Password('password',
        form.notnull,
        form.regexp('[A-Za-z0-9\-]+', 'Must be alpha or digit!'),
        form.Validator('Must be more than 5 characters!', lambda y:len(y)>5)),
    form.Button('Login')
)

class register:
    def GET(self):
        return render.register()
    def POST(self): 
        i = web.input()
        if i.username:
            userInsert = db.insert('users', name=i.username,age=i.age,passwd=hashlib.md5(i.pwd1).hexdigest())
            return render.index(i.username)
        else:
            return render.register()
class login:
    def GET(self): 
        form = loginform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.login(form,user='user')

    def POST(self): 
        form = loginform() 
        if not form.validates(): 
            return render.login(form,user='user')
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            #users = db.select('users',where={'name':form.d.username})
            users = db.query('select * from users where name=$name', vars={'name':form.d.username})
            result = users[0]#None
            #for user in users:
            #    result = user
            if result and result.passwd == hashlib.md5(form.d.password).hexdigest():
                session.username = form.d.username
                raise web.seeother('/')
            return render.login(form,user=None)
class logout:
    def GET(self):
        session.username = None
        raise web.seeother('/')

if __name__=="__main__":
    app.run()
