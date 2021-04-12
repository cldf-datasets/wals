# Releasing WALS as CLDF dataset

- Download the latest comments posted to http://blog.wals.info by
  visiting http://blog.wals.info/wp-admin/edit-comments.php
  and saving all pages listing approved comments as 
  `raw/blog_comments/comments*.html`.
- Run `cldfbench wals.comments` to compile the public info for comments
  to `etc/comments.json`.
- Run `cldfbench makecldf cldfbench_wals.py --glottolog-version v4.3`
- Run `cldfbench cldfreadme cldfbench_wals.py`
- Run `cldfbench readme cldfbench_wals.py`
- Run `cldfbench zenodo cldfbench_wals.py`

