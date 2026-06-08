import os
import runpy
import sys

if __name__ == '__main__':
    # Add backend directory to sys.path
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    sys.path.insert(0, backend_dir)
    
    # Change current working directory to backend so that paths like 'downloads/' and 'history.db' work
    os.chdir(backend_dir)
    
    # Run the actual bot.py script located in the backend folder
    runpy.run_path('bot.py', run_name='__main__')
