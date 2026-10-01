# Arlo Metzger's Portfolio

A static personal portfolio built with HTML, Sass, and vanilla JavaScript and
published to GitHub Pages.

## Pages

- `index.html` redirects the site root to `home.html`.
- `home.html` contains the home page.
- `resume.html`, `portfolio.html`, `blog.html`, and `contact.html` are the main
  site sections.
- `singleBlog.html` and `singlePortfolio.html` are detail-page examples.

The shared sidebar lives in `_includes/sidebar.html`. Each page passes the
active navigation item and theme-toggle ID to that include.

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
