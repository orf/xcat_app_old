from xcat_app.app import app


if __name__ == "__main__":
    app.run(debug=False, host="localhost", threaded=False)
