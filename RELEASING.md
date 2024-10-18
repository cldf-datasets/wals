# Releasing WALS as CLDF dataset

- Run
  ```shell
  cldfbench makecldf cldfbench_wals.py --glottolog-version v5.0
  ```
- Run
  ```shell
  cldfbench cldfreadme cldfbench_wals.py
  ```
- Run
  ```shell
  cldfbench readme cldfbench_wals.py
  ```
- Run
  ```shell
  cldfbench zenodo cldfbench_wals.py
  ```
- Run `pytest`
- Update `CHANGES.md`
- Commit all
- Tag release
