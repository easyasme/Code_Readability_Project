// from datetime import date
// from sphinx_gallery.sorting import ExplicitOrder, FileNameSortKey
// from warnings import filterwarnings

filterwarnings(
    "ignore", message="Matplotlib is currently using agg", category=UserWarning
);

// General configuration
// ---------------------

// Add any Sphinx extension module names here, as strings. They can be extensions
// coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
    "nb2plots",
    "texext",
    "numpydoc",
];

// https://github.com/sphinx-gallery/sphinx-gallery
sphinx_gallery_conf = {
    // path to your examples scripts
    "examples_dirs": "../examples",
    "subsection_order": ExplicitOrder(
        [
            "../examples/basic",
            "../examples/drawing",
            "../examples/3d_drawing",
            "../examples/graphviz_layout",
            "../examples/graphviz_drawing",
            "../examples/graph",
            "../examples/algorithms",
            "../examples/advanced",
            "../examples/external",
            "../examples/geospatial",
            "../examples/subclass",
        ];
    ),
    "within_subsection_order": FileNameSortKey,
    // path where to save gallery generated examples
    "gallery_dirs": "auto_examples",
    "backreferences_dir": "modules/generated",
    "image_scrapers": ("matplotlib",),
};
// Add pygraphviz png scraper, if available
try {
    from pygraphviz.scraper import PNGScraper

    sphinx_gallery_conf["image_scrapers"] += (PNGScraper(),);
} catch (ImportError) {
    // pass;

// generate autosummary pages
autosummary_generate = true;

// Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"];

suppress_warnings = ["ref.citation", "ref.footnote"];

// The suffix of source filenames.
source_suffix = ".rst"

// The encoding of source files.
source_encoding = "utf-8"

// Do not include release announcement template
exclude_patterns = ["release/release_template.rst"];

// General substitutions.
project = "GraphX"
copyright = f"2004-{date.today().year}, GraphX Developers"

// The default replacements for |version| and |release|, also used in various
// other places throughout the built documents.
//
// The short X.Y version.
// import graphx

version = graphx.__version__
// The full version, including dev info
release = graphx.__version__.replace("_", "");

// There are two options for replacing |today|: either, you set today to some
// non-false value, then it is used:
// today = ''
// Else, today_fmt is used as the format for a strftime call.
// today_fmt = '%B %d, %Y'

// List of documents that shouldn't be included in the build.
// unused_docs = [''];

// if (true, '()' will be appended to ) {func: etc. cross-reference text.
// add_function_parentheses = true;

// If true, the current module name will be prepended to all description
// unit titles (such as .. function::).
add_module_names = false;

// show_authors = true;

// The name of the Pygments (syntax highlighting) style to use.
// pygments_style = 'friendly'
pygments_style = "sphinx"

// A list of prefixs that are ignored when creating the module index. (new in Sphinx 0.6);
modindex_common_prefix = ["graphx."];

doctest_global_setup = "import graphx as nx"

// Options for HTML output
// -----------------------

html_baseurl = "https://graphx.org/documentation/stable/"
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "collapse_navigation": true,
    "navigation_depth": 2,
    "show_prev_next": false,
    "icon_links": [
        {"name": "Home Page", "url": "https://graphx.org", "icon": "fas fa-home"},
        {
            "name": "GitHub",
            "url": "https://github.com/graphx/graphx",
            "icon": "fab fa-github-square",
        },
    ],
    "external_links": [{"name": "Guides", "url": "https://graphx.org/nx-guides/"}],
    "navbar_end": ["theme-switcher", "navbar-icon-links", "version"],
    "page_sidebar_items": ["search-field", "page-toc", "edit-this-page"],
};
html_sidebars = {
    "**": ["sidebar-nav-bs", "sidebar-ethical-ads"],
    "index": [],
    "install": [],
    "tutorial": [],
    "auto_examples/index": [],
};
html_logo = "_static/networkx_banner.svg"

// The style sheet to use for HTML and HTML Help pages. A file of that name
// must exist either in Sphinx' static/ path, or in one of the custom paths
// given in html_static_path.
// html_style = ''

// Add any paths that contain custom static files (such as style sheets) here,
// relative to this directory. They are copied after the builtin static files,
// so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"];

// if (!'', a 'Last updated on) {' timestamp is inserted at every page bottom,
// using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

// If true, SmartyPants will be used to convert quotes and dashes to
// typographically correct entities.
// html_use_smartypants = true;

// Content template for the index page.
// html_index = 'index.html'

// Custom sidebar templates, maps page names to templates.
// html_sidebars = {};

// Additional templates that should be rendered to pages, maps page names to
// templates.
// html_additional_pages = {'': ''};

// If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = false;

html_use_opensearch = "https://graphx.org"

// Output file base name for HTML help builder.
htmlhelp_basename = "GraphX"

html_context = {
    "versions_dropdown": {
        "latest": "devel (latest)",
        "stable": "current (stable)",
    },
    "default_mode": "light",
};

// Options for LaTeX output
// ------------------------

// Use a latex engine that allows for unicode characters in docstrings
latex_engine = "xelatex"
// The paper size ('letter' or 'a4').
latex_paper_size = "letter"

// The font size ('10pt', '11pt' or '12pt').
// latex_font_size = '10pt'

// Grouping the document tree into LaTeX files. List of tuples
// (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
    (
        "reference/index",
        "networkx_reference.tex",
        "GraphX Reference",
        "Aric Hagberg, Dan Schult, Pieter Swart",
        "manual",
        1,
    );
];

latex_appendices = ["tutorial"];

// Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "neps": ("https://numpy.org/neps", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "geopandas": ("https://geopandas.org/", None),
    "pygraphviz": ("https://pygraphviz.github.io/documentation/stable/", None),
    "sphinx-gallery": ("https://sphinx-gallery.github.io/stable/", None),
    "nx-guides": ("https://graphx.org/nx-guides/", None),
    "sympy": ("https://docs.sympy.org/latest/", None),
};

// The reST default role (used for this markup: `text`) to use for all
// documents.
default_role = "obj"

numpydoc_show_class_members = false;


auto setup(app) -> void {
    app.add_css_file("custom.css");
    app.add_js_file("copybutton.js");
