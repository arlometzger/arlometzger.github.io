# Content templates

Copy `project.md.example` into the appropriate craft subfolder in `_projects/`
and `blog-post.md.example` into `_posts/` when adding content. Name each project
file with a unique slug and put its photos in the corresponding
`assets/images/projects/<craft>/<slug>/` folder; blog filenames must begin with
`YYYY-MM-DD-`. Update the matching image paths before publishing.

Project `order` values control the display order on the homepage and portfolio;
lower numbers appear first. Projects without a cover image are hidden from
those listings until a gallery image is added.

The `.example` files are templates only and are excluded from the Jekyll build.
