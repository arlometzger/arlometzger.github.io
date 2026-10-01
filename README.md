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
Resume entries live in `assets/js/resume-data.js` and are rendered in Education,
Experience, Skills order. Add a PDF to the repository and set `pdfUrl` in that
file to show the resume download link. Add education entries with `institution`,
`credential`, `dates`, `location`, and `description`; experience entries use
`title`, `organization`, `dates`, `location`, and `description`. Skills are
plain strings in the `skills` array. LinkedIn does not provide a reliable
public profile-sync option for a static GitHub Pages site.

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
