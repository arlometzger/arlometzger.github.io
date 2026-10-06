# Arlo Metzger's Portfolio

A static personal portfolio built with HTML, Sass, and vanilla JavaScript and
published to GitHub Pages.

## Pages

- `index.html` contains the home page.
- `about.html` introduces the maker and their craft interests.
- `resume.html`, `portfolio.html`, `blog.html`, and `contact.html` are the main
  site sections.
- `singleBlog.html` and `singlePortfolio.html` are detail-page examples.

The shared sidebar lives in `_includes/sidebar.html`. Each page passes the
active navigation item and theme-toggle ID to that include. Update your name,
tagline, phone, email, and LinkedIn/Instagram links in
`assets/js/personal-info.js`; that file is loaded by every page with the sidebar.
The sidebar and content pages share the homepage's wide container so the layout
stays aligned across the site.
Add portfolio entries to `assets/js/projects.js`. Each entry should have a
`title`, a `category` (`Woodworking`, `Machining`, `3D modelling`, `Pottery`,
or `Miscellaneous`), and an `image` path. An optional `url` can link to a
project detail page. The portfolio page filters by the selected category, and
the home page shows up to three photos per category. Gallery slots remain
placeholders until project photos are added.
Keep a matching `ArloMetzgerResume.docx` and `ArloMetzgerResume.pdf` in the
repository root. Export both files from the same Google Doc whenever the resume
changes. The DOCX populates the webpage; the checked-in PDF is served as the
download without being converted or modified by the build. Structure the DOCX
with Heading 1 sections named
`Education`, `Experience`, and `Skills`. Use Heading 2 for each school or
company when practical; put each school or company and its location in separate
tab-delimited cells.
For a company with multiple roles, add a separate tab-delimited position and
date line for each role beneath that company; descriptions beneath each role
belong to that role. For education, put the degree and dates on the first body
line under the school. Put each skill on its own paragraph or bullet under
Skills.
GitHub Actions extracts the resume data from the DOCX and verifies that the
matching PDF exists before deployment. Experience descriptions render as
bullets on the website, with all roles grouped under their employer. Keep the
DOCX and PDF filenames in sync with the workflow if you rename either file.

## Project structure

- `assets/sass/` contains the Sass sources, organized by base styles,
  components, layout, and pages.
- `assets/css/main.css` is the compiled stylesheet referenced by the pages.
- `assets/js/` contains page behavior.
- `assets/images/` contains site images and icons.

## Build styles

Install Dart Sass, then compile the Sass entry point from the repository root:

```sh
sass --style=compressed assets/sass/main.scss assets/css/main.css
```

This also updates the source map at `assets/css/main.css.map`.

## Deployment

GitHub Actions builds the site with Jekyll and deploys it to GitHub Pages when
changes are pushed to `master`. The workflow is in
`.github/workflows/jekyll-gh-pages.yml`.
