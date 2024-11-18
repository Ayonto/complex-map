from flask import Flask, render_template, request, send_file
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import re  
import os
import tempfile
import time

app = Flask(__name__)


# def default_function(z):
#     return z**2

#convert the user function input valid funciton 
def process_function_input(function_str):

    function_str = function_str.replace('^', '**')
    
    function_str = re.sub(r'(?<!\w)i(?!\w)', '1j', function_str) 
    function_str = function_str.replace(' ', '')
    # print(function_str)

    replacements = {
        'sin': 'np.sin',
        'cos': 'np.cos',
        'tan': 'np.tan',
        'exp': 'np.exp',
        'log': 'np.log',
        'sqrt': 'np.sqrt',
        'abs': 'np.abs',
        'z_bar': 'np.conj(z)'
    }


    for key, value in replacements.items():
        function_str = re.sub(rf'\b{key}\b', value, function_str)

    return function_str

# evaluate the inputted function string
def evaluate_function(z, function_str):
    try:

        function_str = process_function_input(function_str)       
        w = eval(function_str, {"z": z, "np": np})
        # print(w)
    except Exception as e:
        # print(f"Error in function evaluation: {e}")
        w = None  
    return w


# generate the plot
def generate_plot(function_str, x_min, x_max, y_min, y_max, x_points, y_points):

    x = np.linspace(x_min, x_max, x_points)
    y = np.linspace(y_min, y_max, y_points)
    X, Y = np.meshgrid(x, y)
    
    Z = X + 1j * Y

    W = evaluate_function(Z, function_str)

    if W is None:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f'Mapping of Complex Function f(z) = {function_str} in z-plane and w-plane')


    ax1.set_title("z-plane (Input)")
    ax1.set_xlabel("Re(z)")
    ax1.set_ylabel("Im(z)")
    ax1.grid(True)
    

    for i in range(y_points):
        ax1.plot(x, [y[i]] * len(x), 'b-', lw=0.5)  # horizontal lines


    for i in range(x_points):
        ax1.plot([x[i]] * len(y), y, 'r-', lw=0.5)  # vertical lines


    ax2.set_title("w-plane (Output)")
    ax2.set_xlabel("Re(w)")
    ax2.set_ylabel("Im(w)")
    ax2.grid(True)
    

    for i in range(y_points):
        ax2.plot(W.real[i, :], W.imag[i, :], 'b-', lw=0.5)  # mapped horizontal lines


    for i in range(x_points):
        ax2.plot(W.real[:, i], W.imag[:, i], 'r-', lw=0.5)  # mapped vertical lines

    temp_dir = tempfile.gettempdir()
    plot_path = os.path.join(temp_dir, "plot.png")
    plt.savefig(plot_path)
    plt.close(fig)
    return plot_path


from flask import Flask, render_template, request, send_file
import tempfile
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_path = None
    error_message = None
    function_str = "sin(z)"  # default function

    now = int(time.time())


    x_min = -2
    x_max = 2
    y_min = -2
    y_max = 2
    x_points = 10
    y_points = 10

    

    if request.method == 'POST':
        function_str = request.form.get('function_input', 'sin(z)')
        #slider values from the form
        x_min = float(request.form.get('x_min', -2))
        x_max = float(request.form.get('x_max', 2))
        y_min = float(request.form.get('y_min', -2))
        y_max = float(request.form.get('y_max', 2))
        x_points = int(request.form.get('x_points', 10))
        y_points = int(request.form.get('y_points', 10))
    
    plot_path = generate_plot(function_str, x_min, x_max, y_min, y_max, x_points, y_points)


    if plot_path is None:
        error_message = "The function might be incorrect. Please check the syntax and try again."

    return render_template(
        'index.html', 
        plot_path=plot_path, 
        error_message=error_message, 
        function_str=function_str, 
        now=now,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        x_points=x_points,
        y_points=y_points
    )

@app.route('/plot.png')
def plot():

    temp_dir = tempfile.gettempdir()
    plot_path = os.path.join(temp_dir, "plot.png")
    return send_file(plot_path, mimetype='image/png')



if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
