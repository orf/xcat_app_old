import os
import time
import sys
import platform
import site

packages = site.getsitepackages()[0]
if packages not in sys.path:
    sys.path.append(packages)

from flask import Flask, request, render_template, Response

app = Flask(__name__)

if "__file__" in locals():
    saxon_jar = os.path.join(os.path.dirname(__file__), "saxon", "Saxon-HE.jar")
else:
    saxon_jar = sys.path.append(os.path.join("saxon", "Saxon-HE.jar"))

library = "library.xml"

XPATH_1 = "--xpath1" in sys.argv
IS_JYTHON = platform.python_implementation() == "Jython"

if IS_JYTHON:
    sys.path.append(saxon_jar)
    from javax.xml.xpath import *
    from net.sf.saxon.s9api import *
    from org.xml.sax import InputSource
    from javax.xml.transform.sax import SAXSource
    from net.sf.saxon.xpath import *


if XPATH_1:
    print("Using XPath 1.0")
else:
    print("Using XPath 2.0 via {path}".format(path=saxon_jar))


@app.route("/rental")
def rental():
    id = request.args["id"]
    rental_query = "/*/rentals/*/*[@id={id}]".format(id=id)
    result = run_xpath_query(rental_query)

    if len(result) == 0:
        return Response(status=404)
    else:
        return render_template("rental.jinja2", rental=result[0])


@app.route("/")
def index():
    orig_title_query = request.args.get("title", "")
    search_type = request.args.get("type", "*")
    rent_days = request.args.get("rent_days", "*")

    title_query = "contains(title/text(), '{}') ".format(orig_title_query) \
        if orig_title_query else "true()"

    xpath_filter = "{title_query} and rent_days={rent_days}" \
        .format(title_query=title_query, rent_days=rent_days)

    xpath_query = "/*/rentals/{type}/*[{filter}]".format(type=search_type,
                                                         filter=xpath_filter)

    results = run_xpath_query(xpath_query)

    response = Response(render_template("index.jinja2", results=results, query=orig_title_query))
    response.headers["X-query"] = xpath_query

    return response


def run_xpath_query(query):
    functions = {
        True: run_xpath1_query_jython if IS_JYTHON else run_xpath1_query_blunt,
        False: run_xpath2_query_jython if IS_JYTHON else run_xpath2_query_blunt
    }

    results, run_time, error = functions[XPATH_1](query)

    if error:
        print(error.decode())

    print("[{time:1.4f}] {cmd}".format(time=run_time, cmd=query))
    return results


def getChildren(node):
    axis_iterator = node.iterateAxis(Axis.getAxisNumber(Axis.CHILD))

    while True:
        child = axis_iterator.current()
        if child is not None:
            if child.displayName != "":
                yield child

        if not axis_iterator.moveNext():
            break


def run_xpath1_query_jython(query):
    return run_xpath2_query_jython(query)  # Haven't


def run_xpath2_query_jython(query):
    t1 = time.time()
    xpf = XPathFactoryImpl()
    xpe = xpf.newXPath()

    input_s = InputSource(str(library))
    sax_source = SAXSource(input_s)
    config = xpf.getConfiguration()

    doc = config.buildDocument(sax_source)

    expression = xpe.compile(query)
    results = expression.evaluate(doc, XPathConstants.NODESET)
    return [
        parse_item_java(r) for r in results
    ], time.time() - t1, ""


def run_xpath1_query_blunt(query):
    from lxml import etree

    t1 = time.time()
    with open("library.xml", "rb") as fd:
        tree = etree.parse(fd)
    try:
        results = tree.xpath(query)
        return [
                   parse_item(result) for result in results
                   ], time.time() - t1, ""
    except Exception:
        return [], 0, ""


def run_xpath2_query_blunt(query):
    """
    This executes an xpath query against library.xml. It's horrible and relies on calling an external .jar file,
    which makes it very expensive (0.4s per query). Oh well.
    """
    from sarge import run, Capture
    from lxml import etree
    library_arg = "-s:{library} ".format(library=library)
    args = ["java", "-Xms50m", "-cp", str(saxon_jar), "net.sf.saxon.Query", library_arg, "-", "-wrap", "-ext:off"]

    start = time.time()
    p = run(args, stdout=Capture(), stderr=Capture(), cwd=os.getcwd(), input=query)
    output = p.stdout.read()
    error = p.stderr.read()

    try:
        tree = etree.fromstring(output)
        returner = [
            parse_item(result.find("./*")) for result in tree.getchildren()
            ]
    except Exception:
        returner = []

    end = time.time()
    return returner, end - start, error


def parse_item(result):
    children = result.getchildren()
    returner = {
        child.tag: child.text for child in children
        }
    returner["id"] = result.attrib["id"]
    return returner


def parse_item_java(result):
    children = result.iterateAxis(Axis.CHILD.axisNumber)
    returner = {}
    while children.hasNext():
        child = children.next()
        if child.displayName:
            returner[child.displayName] = child.getStringValue()

    returner["id"] = result.getAttributeValue("", "id")
    return returner