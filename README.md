# Arlo Metzger's Craft Portfolio

A static portfolio and resume built with Jekyll, HTML, Sass, and vanilla
JavaScript, and published to GitHub Pages.

## Repository map

| Path | Purpose |
| --- | --- |
| `_config.yml` | Jekyll collections, permalinks, and site metadata |
| `_includes/` | Shared Liquid snippets, including the sidebar and project galleries |
| `_layouts/` | Reusable page shells for projects and blog posts |
| `_projects/` | One Markdown document per portfolio project |
| `_posts/` | One dated Markdown document per blog post |
| `assets/images/projects/<slug>/` | Cover and detail photos for a project |
| `assets/images/blog/<slug>/` | Cover and in-article photos for a post |
| `assets/images/icon/` | Shared icons |
| `assets/images/img/` | Existing site/profile images |
| `assets/css/` | Stylesheets served by the site |
| `assets/sass/` | Sass source, organized into base, components, layout, and pages |
| `assets/js/` | Browser behavior for site navigation, project filtering, and blog listing |
| `docs/content-templates/` | Copyable Markdown templates for new projects and posts |
| `scripts/` | Build scripts, including the resume data generator |
| `tests/` | Automated tests for build scripts |

The existing main pages stay at the repository root to preserve their URLs.
New project and post detail pages are generated from Jekyll collections using
the shared layouts in `_layouts/`.

## Add a project

1. Copy `docs/content-templates/project.md.example` to `_projects/<slug>.md`.
   Use a short, lowercase, hyphen-separated slug, such as
   `_projects/wooden-stool.md`.
2. Fill in the front matter. `title`, `category`, `date`, `description`, and
   `gallery` are expected. Add one `image` and descriptive `alt` for each
   gallery photo. The first gallery image is used as the portfolio-card cover
   and first homepage preview. `image_description` adds a caption below the
   gallery.
3. Create `assets/images/projects/<slug>/` and add the cover and any detail
   photos there. Use optimized JPG or WebP for photos; descriptive filenames
   make them easier to maintain.
4. Update the gallery image paths. Add an optional narrative below the front
   matter as Markdown; leave it empty for a photo-only project page.
5. Build the site or preview it locally, then commit the Markdown and image
   files together.

Use one of these exact categories so the portfolio filters and home galleries
work: `Woodworking`, `Machining`, `3D modelling`, `Pottery`, or
`Miscellaneous`. Set each image path to a site-root path, for example
`/assets/images/projects/wooden-stool/cover.jpg`. The project page is generated
at `/portfolio/wooden-stool/`; cards and home galleries link to it
automatically. Gallery photos keep their original aspect ratios, fit inside
responsive columns, and are not cropped.

## Add a blog post

1. Copy `docs/content-templates/blog-post.md.example` to
   `_posts/YYYY-MM-DD-<slug>.md`, for example
   `_posts/2026-10-06-sharpening-a-chisel.md`. The date in the filename is
   required by Jekyll.
2. Set the title, date, short description, category, author, cover image, and
   cover image alt text in the front matter.
3. Create `assets/images/blog/<slug>/` for the cover and any photos within the
   post. Reference each image with a site-root path in Markdown.
4. Write the post body in Markdown. The post appears on the blog listing and
   gets its own `/blog/<slug>/` page automatically.

Jekyll uses the post date and filename to determine ordering and the post URL.
Use a unique slug and keep image paths in sync if you rename a post.
Posts in `_posts/` dated today or earlier are published with the next successful
site deployment. Jekyll does not publish future-dated posts yet. Keep draft
writing outside `_posts/` until it is ready to appear on the site.

## Images and other assets

- Keep project and blog photos in their matching slug folders, not in the
  shared `assets/images/img/` directory.
- Give every informative image useful alt text. Use an empty alt value only
  for purely decorative images.
- Keep image dimensions reasonable for the web and use descriptive filenames.
- Keep shared interface icons in `assets/images/icon/`.
- Existing template/demo images are retained in `assets/images/img/`; new
  project and post content should use the dedicated folders above.

## Add another page

New project and blog content should use the collections above instead of
copying a detail-page HTML file. Their generated pages share
`_layouts/default.html`, which provides the responsive site shell and sidebar.
Use `_layouts/project.html` or `_layouts/post.html` for their respective
content types. Add reusable Liquid markup to `_includes/` rather than
duplicating it across multiple pages.

For a standalone root-level page, preserve the existing `.html` URL, include
the standard front matter (`title`, `description`, and `nav_section`), and use
`layout: default` where appropriate. `nav_section` should match the active
sidebar item (`home`, `portfolio`, `resume`, `blog`, `contact`, or `about`).
Use `relative_url` for links and assets in Liquid templates so the site also
works when hosted below a domain root.

## Personal information

Update your name, tagline, phone, email, and LinkedIn/Instagram links in
`assets/js/personal-info.js`. It is loaded by pages that include the shared
sidebar.

## Resume

Keep matching `ArloMetzgerResume.docx` and `ArloMetzgerResume.pdf` files in the
repository root. Export both from the same source document whenever the resume
changes. The DOCX populates the webpage; the checked-in PDF is served as the
download and is not converted or modified by the build.

Structure the DOCX with Heading 1 sections named `Education`, `Experience`,
and `Skills`. Use Heading 2 for each school or company when practical; put each
school or company and its location in separate tab-delimited cells.

For a company with multiple roles, add a separate tab-delimited position and
date line for each role beneath that company; descriptions below each role
belong to that role. For education, put the degree and dates on the first body
line under the school. Put each skill on its own paragraph or bullet under
Skills.

GitHub Actions extracts the resume data from the DOCX and verifies that the
matching PDF exists before deployment. Experience descriptions render as
bullets on the website, with roles grouped under their employer. If either
resume file is renamed, update `.github/workflows/jekyll-gh-pages.yml` and the
related tests.

## Styles and local preview

Edit Sass in `assets/sass/` and keep the compiled
`assets/css/main.css` in sync. With Dart Sass installed, compile from the
repository root:

```sh
sass --style=compressed assets/sass/main.scss assets/css/main.css
```

The archived heading comparison is available at
[`docs/header-style-samples.html`](docs/header-style-samples.html), with a
full-page PNG at `assets/images/reference/header-style-samples.png`.

GitHub Pages builds the site with Jekyll through
`.github/workflows/jekyll-gh-pages.yml` when changes are pushed to `master`.
Preview the generated site locally with Jekyll before publishing when possible.
