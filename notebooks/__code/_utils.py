from IPython.display import HTML, display


def js_alert(m):
    js = "<script>alert('%s');</script>" % m
    display(HTML(js))
