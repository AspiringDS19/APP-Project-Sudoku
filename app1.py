from flask import Flask, render_template, request, session, jsonify
import random
import time

app = Flask(__name__)
app.secret_key = '111111'

# Define the symbols for the grid sizes
latin_symbols_4x4 = ['A', 'B', 'C', 'D']
latin_symbols_6x6 = ['A', 'B', 'C', 'D', 'E', 'F']
latin_symbols_9x9 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

def is_valid(sudoku, row, col, symbol, size):
    for i in range(size):
        if sudoku[row][i] == symbol or sudoku[i][col] == symbol:
            return False
    return True

def fill_sudoku(sudoku, size, symbols):
    for row in range(size):
        for col in range(size):
            if sudoku[row][col] == '':
                random_symbols = random.sample(symbols, len(symbols))  # Randomize symbols
                for symbol in random_symbols:  
                    if is_valid(sudoku, row, col, symbol, size):
                        sudoku[row][col] = symbol
                        if fill_sudoku(sudoku, size, symbols):
                            return True
                        sudoku[row][col] = ''  # Backtrack
                return False
    return True

def generate_sudoku(size):
    if size == 4:
        symbols = latin_symbols_4x4
    elif size == 6:
        symbols = latin_symbols_6x6
    else:
        symbols = latin_symbols_9x9

    grid = [['' for _ in range(size)] for _ in range(size)]
    fill_sudoku(grid, size, symbols)

    # Clear random cells
    for _ in range(size):  # Clear 'size' cells for user input
        row, col = random.randint(0, size - 1), random.randint(0, size - 1)
        grid[row][col] = ''  # Clear the cell for user input

    return grid

# Hint system
def provide_hint(sudoku_grid, size):
    while True:
        row, col = random.randint(0, size - 1), random.randint(0, size - 1)
        if sudoku_grid[row][col] != '':
            return row, col, sudoku_grid[row][col]

@app.route('/')
def home():
    return render_template('sudoku.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    size = int(request.form.get('grid_size'))
    sudoku_grid = generate_sudoku(size)
    
    session['sudoku_grid'] = sudoku_grid  # Save the grid in session
    session['grid_size'] = size
    session['last_move_time'] = time.time()
    
    return render_template('sudoku.html', sudoku_grid=sudoku_grid, size=size)

@app.route('/get_hint', methods=['POST'])
def get_hint():
    sudoku_grid = session.get('sudoku_grid')
    size = session.get('grid_size')
    
    hint = provide_hint(sudoku_grid, size)
    row, col, symbol = hint
    
    # Format hint message
    hint_message = f"Hint: Try placing '{symbol}' at Row: {row + 1}, Column: {col + 1}."
    
    return jsonify({'hint': hint_message})

@app.route('/check_solution', methods=['POST'])
def check_solution():
    try:
        data = request.json  # Get the incoming JSON data
        print("Received data:", data)  # Debug: Log the received data

        grid_size = data.get('grid_size')  # Retrieve grid size
        user_grid = data.get('user_grid')  # Retrieve the grid data

        # Debug: Log the grid size and user grid
        print(f"Grid size: {grid_size}")
        print(f"User grid: {user_grid}")

        if not grid_size or not user_grid:
            return jsonify({'result': False, 'message': 'Missing grid size or grid data!'}), 400

        # Ensure the grid matches the expected size
        if len(user_grid) != int(grid_size) or any(len(row) != int(grid_size) for row in user_grid):
            return jsonify({'result': False, 'message': 'Grid size mismatch!'}), 400

        # Check solution logic here

        return jsonify({'result': True, 'message': 'Solution is correct!'})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'result': False, 'message': 'An internal error occurred.'}), 500




if __name__ == '__main__':
    app.run(debug=True)
