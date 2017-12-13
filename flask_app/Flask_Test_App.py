from flask import Flask, flash, redirect, render_template, request, session, abort
import random,os,ast,prettytable
from flask_app import forms

import AATC_Server_002 as AATC_Server
import HedaBot
COMMANDS = HedaBot.CreateCommandDictionary()
COMMANDS["AddFlight"][2]["Type"] = lambda x: HedaBot.SplitWaypoints(x,":")
COMMANDS["AddFlight"][2]["Query"] = COMMANDS["AddFlight"][2]["Query"].replace("returns","colons")

app = Flask(__name__)
app.config.from_object('config')





@app.route("/")
def home():
##    session["UserID"] = random.randint(0,1000)
    return render_template("base.html",user = {"Username":session.get("UserID"), "UserID":session.get("UserID")},Commands = COMMANDS)

@app.route("/help")
def help_page():
    return render_template("help.html",name = session.get("UserID"),user = {"Username":session.get("UserID"), "UserID":session.get("UserID")})

@app.route("/base")
def base():
    return render_template("base.html",user = {"Username":session.get("UserID"), "UserID":session.get("UserID")})

@app.route("/quote")
def quote():
    quotes = ObtainQuote(3)
    return render_template("quote.html", quotes = quotes,user = {"Username":session.get("UserID"), "UserID":session.get("UserID")})


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    
    if form.validate_on_submit():
        print("Loggin in ...")
        if form.Username.data == form.Password.data:
            session["UserID"] = form.Username.data
        else:
            session["UserID"] = -1
    return render_template("LoginForm.html",title = "Login",form = form,user = {"Username":session.get("UserID"), "UserID":session.get("UserID")})


@app.route("/dyno", methods=['GET', 'POST'])
def dyno():
    items = [{"name":"Username"},{"name":"Password"}]

    fields = [{"name":"Username","form":forms.wtforms.StringField('Username', validators=[forms.DataRequired()])},
              {"name":"Password","form":forms.wtforms.StringField('Password', validators=[forms.DataRequired()])}]
    #form = forms.DynoForm(fields = items)
    form = forms.update_form(fields)
    print(form.__dict__)
    
    
    if form.validate_on_submit():
        print("Loggin in ...")
        print(form.fields.data)
        if form.Username.data == form.Password.data:
            session["UserID"] = form.Username.data
        else:
            session["UserID"] = -1

    #print(form.fields.__dict__)
    return render_template("DynamicForm.html",title = "Login",form = form,user = {"Username":session.get("UserID"), "UserID":session.get("UserID")},fields = fields)


@app.route("/command/<string:command>",methods=['GET', 'POST'])
def Dynamic_Form(command):
    if command not in COMMANDS:
        return "FAILURE COMMAND DOES NOT EXIST"

    Fields = Generate_Fields(command)
    form = forms.update_form(Fields)

    if form.validate_on_submit():
        packet = Evaluate_Form(command,form)
        WebConnection = AATC_Server.WebConnection(session.get("UserID",-1))
        Sucess,Message,Data = WebConnection.Main(packet)

        if command == "Login":
            session["UserID"] = Data
            Data = []

        rendered = RenderResults(Sucess,Message,Data)
        print(rendered)

        return render_template("DynamicForm2.html",title = "Output",form = form,user = {"Username":session.get("UserID"), "UserID":session.get("UserID")},fields = Fields ,Commands = COMMANDS, OUTPUT = True, rendered_result = rendered)

    return render_template("DynamicForm2.html",title = "command",form = form,user = {"Username":session.get("UserID"), "UserID":session.get("UserID")},fields = Fields,Commands = COMMANDS)






def Generate_Fields(command):
    
    Queries = COMMANDS[command]
    Fields = []
    for x in range(1,len(Queries)+1):
        query_name = Queries[x]["Query"]
        field = {"name":query_name ,"form":forms.wtforms.StringField(query_name, validators=[forms.DataRequired()])}
        Fields.append(field)

    return Fields


def Evaluate_Form(command,form):
    Queries = COMMANDS[command]
    Arguments = []
    for x in range(1,len(Queries)+1):
        Arguments.append( Queries[x]["Type"](form.__dict__[Queries[x]["Query"]].data))
    
    packet = (command,Arguments)
    return packet
    






def RenderResults(Sucess,Message,Data = None):
    render = ""
    render += "Sucess >>"+str(Sucess)+"\n"
    render += "Message >>"+str(Message) +"\n"
    if Data not in [None,[]]:
        try:
            Columns = ast.literal_eval(Message)
            Table = prettytable.PrettyTable(Columns)
            for row in Data:
                Table.add_row(row)
            render += str(Table)
        except Exception as e:
            render += "Error creating asthetic table"+str(e) +"\n"
            for row in Data:
                render += str(row)+"\n"
            render += ""
    rendered = render.split("\n")
    return rendered


                    


##def ObtainQuote(number = 1):
##    with open(os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)),"SkyrimDialogue.txt"),"r") as f:
##        for i,line in enumerate(f):
##            pass
##
##    responses = []
##    for f in range(number):
##        lineNum = random.randint(0,i+1)
##        with open(os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)),"SkyrimDialogue.txt"),"r") as f:
##            for x in range(lineNum):
##                line = f.readline()
##            responses.append( line.rstrip().split("\t")[-1:][0])
##    return responses


def main_app(app):
    app.secret_key = "abcewhfuhiwuhef"
    app.run(host = "0.0.0.0")

if __name__ == "__main__":
    main_app(app)
