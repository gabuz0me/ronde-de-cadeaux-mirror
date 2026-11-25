from importlib.metadata import metadata, version

_module_name = "ronde-de-cadeaux"
__version__ = version(_module_name)

_project_urls = metadata(_module_name).get_all("Project-URL") or []
__homepage__ = next(
    (url.split(", ", 1)[1] for url in _project_urls if url.startswith("Homepage, ")),
    "",
)
