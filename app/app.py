from flask import Flask, render_template
from tp import solveConstraintProblem
app = Flask(__name__)


@app.route('/')
def index():
    # data={
    #     'titulo':"Index",
    #     'bienvenida':"!saludos!"
    # }
    data=solveConstraintProblem();
    print(data[0].id)
    return render_template('index.html',data=data)


if __name__ == '__main__':
    app.run()