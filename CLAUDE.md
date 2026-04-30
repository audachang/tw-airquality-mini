> Scaffold a data analysis project in the current directory:
    data/
      raw/         (read-only original data; add .gitkeep)
      processed/   (cleaned outputs; add .gitkeep)
    notebooks/
      01_explore.ipynb   (starter notebook with title + pandas import)
    src/
      __init__.py
      load_data.py       (stub: load_csv(path) -> pd.DataFrame)
      clean_data.py      (stub: clean(df) -> pd.DataFrame)
    reports/             (HTML / PDF outputs; add .gitkeep)
    README.md            (title, one-paragraph description, How to run)
    .gitignore           (Python, Jupyter, venv, OS, data/raw/*.csv)
    requirements.txt     (keep existing entries, just confirm)
 
  Do not overwrite requirements.txt. Use placeholder content.