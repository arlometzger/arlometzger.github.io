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
Use `ArloMetzgerResume.docx` as the resume source. Export the Google Doc as
Microsoft Word (.docx), then structure it with Heading 1 sections named
`Education`, `Experience`, and `Skills`. Use Heading 2 for each school or role;
paragraphs beneath it become the entry details. Put each skill on its own
paragraph or bullet under Skills. GitHub Actions extracts those sections into
the website and converts the same DOCX to `ArloMetzgerResume.pdf` using
LibreOffice. No browser plugin or external resume service is required. The
existing PDF remains the published download until the DOCX source is added.

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
