from xcat_app.app import app
import sys

if "--test" in sys.argv:
    sys.exit(1)

if __name__ == "__main__":
    app.run(debug=False, host="localhost", threaded=False)
