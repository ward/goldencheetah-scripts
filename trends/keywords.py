import tempfile
import pathlib


def get_runs():
    try:
        DATA = GC.seasonMetrics()
        runs = []
        for i in range(len(DATA["Distance"])):
            if DATA["Sport"][i] == "Run":
                run = (DATA["date"][i], DATA["Keywords"][i])
                runs.append(run)
    except NameError:
        runs = []
    return runs


def count_keywords(runs):
    all_keywords = {}
    for run in runs:
        keywords = run[1].split(", ")
        for keyword in keywords:
            if keyword == "":
                continue
            if keyword not in all_keywords:
                all_keywords[keyword] = {
                    "word": keyword,
                    "counter": 1,
                    "last_time": run[0],
                }
            else:
                all_keywords[keyword] = {
                    "word": keyword,
                    "counter": all_keywords[keyword]["counter"] + 1,
                    "last_time": run[0],
                }

    all_keywords = list(all_keywords.values())
    all_keywords = sorted(all_keywords, key=lambda keyword: keyword["word"])
    all_keywords = sorted(
        all_keywords, key=lambda keyword: keyword["counter"], reverse=True
    )

    return all_keywords


def write_keywords(f, keywords):
    header_a = "<!DOCTYPE html>" "<html>" "<head>"
    header_b = "</head>" "<body>"
    footer = "</body>" "</html>"
    f.write(header_a)
    # write_css(f)
    f.write(header_b)
    f.write("<table>")
    for keyword in keywords:
        f.write(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                keyword["word"], keyword["counter"], keyword["last_time"]
            )
        )
    f.write("</table>")
    f.write(footer)


def output_file(write_function):
    with tempfile.NamedTemporaryFile(
        mode="w+t", prefix="GC_", suffix=".html", delete=False
    ) as tmp_f:
        write_function(tmp_f)
        NAME = pathlib.Path(tmp_f.name).as_uri()
        print(NAME)
    try:
        GC.webpage(NAME)
    except NameError:
        pass


keywords = count_keywords(get_runs())
output_file(lambda f: write_keywords(f, keywords))
