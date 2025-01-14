from flask import Flask, request, render_template_string
import sys
import subprocess
import pkg_resources

app = Flask(__name__)

# Simplified HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Package Checker</title>
</head>
<body>
    <h1>System Information</h1>
    <pre>{{ debug_info }}</pre>
    
    <h2>Install Packages</h2>
    <form action="/install" method="post">
        <input type="submit" value="Install Required Packages">
    </form>
    
    {% if message %}
    <h2>Message:</h2>
    <pre>{{ message }}</pre>
    {% endif %}
</body>
</html>
'''

def get_installed_packages():
    return [f"{pkg.key} {pkg.version}" for pkg in pkg_resources.working_set]

@app.route('/')
def index():
    debug_info = "Python Information:\n"
    debug_info += f"Python Version: {sys.version}\n"
    debug_info += f"Python Path: {sys.path}\n\n"
    
    debug_info += "Installed Packages:\n"
    for pkg in get_installed_packages():
        debug_info += f"{pkg}\n"
    
    return render_template_string(HTML_TEMPLATE, debug_info=debug_info)

@app.route('/install', methods=['POST'])
def install_packages():
    try:
        # Install required packages using pip
        packages = [
            'setuptools',
            'wheel',
            'decorator==4.4.2',
            'imageio==2.9.0',
            'imageio-ffmpeg==0.4.5',
            'numpy==1.19.5',
            'proglog==0.1.9',
            'requests==2.25.1',
            'tqdm==4.64.1',
            'moviepy==1.0.3'
        ]
        
        message = "Installation Log:\n"
        for package in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', package])
                message += f"Successfully installed {package}\n"
            except subprocess.CalledProcessError as e:
                message += f"Failed to install {package}: {str(e)}\n"
        
        # Try importing moviepy to verify installation
        try:
            import moviepy.editor
            message += "\nMoviePy successfully imported!"
        except ImportError as e:
            message += f"\nMoviePy import failed: {str(e)}"
        
        return render_template_string(HTML_TEMPLATE, 
            debug_info=get_installed_packages(), 
            message=message)
            
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, 
            debug_info=get_installed_packages(), 
            message=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)