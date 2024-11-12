from flask import Flask, render_template, request
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import re  
import os

app = Flask(__name__)


def default_function(z):
    return z**2

#convert the user function input valid funciton 
def process_function_input(function_str):
    # replacing ^ with ** 
    function_str = function_str.replace('^', '**')

    # replacements for common functions
    replacements = {
        'sin': 'np.sin',
        'cos': 'np.cos',
        'tan': 'np.tan',
        'exp': 'np.exp',
        'log': 'np.log',
        'sqrt': 'np.sqrt',
        'abs': 'np.abs'
    }

    # replacing functions with numpy 
    for key, value in replacements.items():
        function_str = re.sub(rf'\b{key}\b', value, function_str)

    return function_str

# evaluate the inputted function string
def evaluate_function(z, function_str):
    try:

        function_str = process_function_input(function_str)
       
        w = eval(function_str, {"z": z, "np": np})
    except Exception as e:
        # print(f"Error in function evaluation: {e}")
        w = None  
    return w

# generate the plot
def generate_plot(function_str):
    # grid in the z-plane
    x_min, x_max, x_points = -2, 2, 10
    y_min, y_max, y_points = -2, 2, 10

    x = np.linspace(x_min, x_max, x_points)
    # print(x.shape)
    # print(x)
    y = np.linspace(y_min, y_max, y_points)
    # print(y)
    X, Y = np.meshgrid(x, y)  
    # print(X)
    
    Z = X + 1j * Y  # combine into complex grid

    W = evaluate_function(Z, function_str)
    # print(type(W))
    # print(W)

    if W is None:
        return None 


    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f'Mapping of Complex Function f(z) = {function_str} in z-plane and w-plane')

    # plot z-plane
    ax1.set_title("z-plane (Input)")
    ax1.set_xlabel("Re(z)")
    ax1.set_ylabel("Im(z)")
    ax1.grid(True)
    for i in range(x_points):
        ax1.plot(x, [y[i]] * len(x), 'b-', lw=0.5)  # horizontal lines
        ax1.plot([x[i]] * len(y), y, 'r-', lw=0.5)  # vertical lines

    # plot mapped w-plane
    ax2.set_title("w-plane (Output)")
    ax2.set_xlabel("Re(w)")
    ax2.set_ylabel("Im(w)")
    ax2.grid(True)
    for i in range(x_points):
        ax2.plot(W.real[i,:], W.imag[i, :], 'b-', lw=0.5)  # mapped horizontal lines
        ax2.plot(W.real[:,i], W.imag[:, i], 'r-', lw=0.5)  # mapped vertical lines


    plot_path = "static/plot.png"
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(plot_path)
    plt.close(fig)  

    return plot_path


@app.route('/', methods=['GET', 'POST'])
def index():
    plot_path = None
    error_message = None


    function_str = "sin(z)"  # default function 

    if request.method == 'POST':
        function_str = request.form.get('function_input', 'sin(z)')

    plot_path = generate_plot(function_str)

    if plot_path is None:
        error_message = "The function might be incorrect. Please check the syntax and try again."

    return render_template('index.html', plot_path=plot_path, error_message=error_message, function_str=function_str)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
