from xcat_app.app import app, run_xpath2_query_jython
import sys

if "--test" in sys.argv:
    sys.exit(1)

if "--shell" in sys.argv:
    while True:
        query = raw_input()
        print(run_xpath2_query_jython(query))

if __name__ == "__main__":
    app.run(debug=False, host="localhost", threaded=False, port=8080)
