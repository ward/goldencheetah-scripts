import os


def get_files(folder):
    files = os.listdir(folder)
    return filter(lambda x: x != "index.html", sorted(files))


def make_css_tag():
    with open("index.css", "r") as css_file:
        contents = css_file.read()
        return '<style type="text/css">' + contents + "</style>"


def write_file_listing(f, filenames):
    f.write("<nav class='file-listing'>")
    for filename in get_files("./output/"):
        f.write('<a href="{}">{}</a>'.format(filename, filename))
    f.write("</nav>")


def write_index(f):
    header = (
        "<!DOCTYPE html>"
        + "<html>"
        + "<head>"
        + '<meta charset="utf-8" />'
        + "<title>Running Graphs</title>"
        + '<meta name="viewport" content="width=device-width, initial-scale=1" />'
        + make_css_tag()
        + "</head>"
        + "<body>"
    )
    footer = "</body>" "</html>"
    f.write(header)
    f.write("<h1>Running Graphs</h1>")
    write_file_listing(f, get_files("./output/"))
    f.write(footer)


NAME = "./output/index.html"
with open(NAME, "w") as tmp_f:
    write_index(tmp_f)
