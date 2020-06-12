# Releasing WALS as CLDF dataset

- Download the latest comments posted to http://blog.wals.info by
  visiting http://blog.wals.info/wp-admin/edit-comments.php
  and saving all comments pages as `raw/WALS_comments*.html`.
- Run `cldfbench wals.comments` to compile the public info for comments
  to `etc/comments.json`.
- Run `cldfbench makecldf`
