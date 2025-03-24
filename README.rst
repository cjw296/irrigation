.. code-block:: bash

  conda activate irrigation
  cd ~/vcs/git/irrigation/
  jupyter notebook

  python download.py --start 2023-04-01 1hour_Level2 Rain --force
  python download.py --start 2023-04-01 climate_extract_cgi RR
