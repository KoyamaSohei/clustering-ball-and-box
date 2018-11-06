from flask import Flask,Response,send_file
import os.path
import ctrlColor
import io


app = Flask(__name__)

app.config.from_object(__name__)

def root_dir():  # pragma: no cover
  return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
  try:
    src = os.path.join(root_dir(), filename)
      # Figure out how flask returns static files
      # Tried:
      # - render_template
      # - send_file
      # This should not be so non-obvious
    return open(src).read()
  except IOError as exc:
    return str(exc)

@app.route('/', methods=['GET'])
def index():
  content = get_file('index.html')
  print(content)
  return Response(content, mimetype="text/html")

@app.route('/<string:color>/<int:min>/<int:max>')
def post(color,min,max):
  print(color,min,max)
  ctrlColor.search(color,min,max)
  return send_file(color + '.png', mimetype="image/png")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
  mimetypes = {
    ".css": "text/css",
    ".html": "text/html",
    ".js": "application/javascript",
  }
  complete_path = os.path.join(root_dir(), path)
  ext = os.path.splitext(path)[1]
  mimetype = mimetypes.get(ext, "text/html")
  content = get_file(complete_path)
  return Response(content, mimetype=mimetype)

if __name__ == '__main__':  # pragma: no cover
  app.run(port=8000,debug=True)