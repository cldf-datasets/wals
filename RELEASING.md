# Releasing WALS as CLDF dataset

- Clone the dataset and install dependencies:
  ```shell
  git clone https://github.com/cldf-datasets/wals
  cd wals
  pip install -e .[test]
  ```

- Run
  ```shell
  cldfbench makecldf cldfbench_wals.py --glottolog-version v5.3
  cldf validate cldf --with-cldf-markdown
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
