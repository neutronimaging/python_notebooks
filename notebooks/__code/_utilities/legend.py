from IPython.display import display
from IPython.display import HTML


def legend() -> None:
    display(HTML("<hr style='height:2px'/>"))
    display(HTML("<h2>Legend</h2>"))
    display(
        HTML(
            "<ul>"
            "<li><b><font color='red'>Mandatory steps</font></b> must be performed to ensure proper data processing.</li>"
            "<li><b><font color='orange'>Optional but recommended steps</font></b> are not mandatory but should be performed to ensure proper data processing.</li>"
            "<li><b><font color='purple'>Optional steps</font></b> are not mandatory but highly recommended to improve the quality of your data processing.</li>"
            "</ul>"
        )
    )
    display(HTML("<hr style='height:2px'/>"))
