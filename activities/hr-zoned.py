import plotly
import plotly.graph_objs as go
import math
import tempfile
import pathlib

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    class GC:
        @classmethod
        def activity(cls) -> Any: ...
        @classmethod
        def webpage(cls, _: str) -> Any: ...


def secs_to_hms(s):
    if math.isnan(s):
        return s
    s = math.floor(s)
    h = math.floor(s / 3600)
    s = s % 3600
    m = math.floor(s / 60)
    s = s % 60
    if h > 0:
        return "{}:{:0>2}:{:0>2}".format(h, m, s)
    else:
        return "{}:{:0>2}".format(m, s)


heartrates_map = {
    int(s): h for s, h in zip(GC.activity()["seconds"], GC.activity()["heart.rate"])
}
seconds = list(range(max(heartrates_map.keys())))
heartrates = [heartrates_map.get(s) for s in seconds]
hovertext = []


for hr, sec in zip(heartrates, seconds):
    s = secs_to_hms(sec)
    hovertext.append(f"({s}, {hr})")


###########################################
# Actual plotting
temp_file = tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_", suffix=".html", delete=False
)
f = plotly.offline.plot(
    {
        "data": [
            go.Scatter(
                x=seconds,
                y=heartrates,
                name="HR",
                text=hovertext,
                hoverinfo="text",
                line=dict(color="red"),
            ),
        ],
        "layout": go.Layout(
            xaxis=dict(title="seconds elapsed time"),
            yaxis=dict(title="BPM", range=[120, 190]),
            shapes=[
                dict(
                    type="line",
                    xref="paper",
                    x0=0,
                    x1=1,
                    yref="y",
                    y0=y,
                    y1=y,
                    line=dict(color="#666666", dash="dash"),
                )
                for y in [144, 154, 170, 190]
            ],
        ),
    },
    auto_open=False,
    filename=temp_file.name,
)

GC.webpage(pathlib.Path(f).as_uri())
