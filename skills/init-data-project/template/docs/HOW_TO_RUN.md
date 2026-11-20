# How to run — <PROJECT_NAME>

Once per session:

```powershell
conda activate TODO_ENV_NAME
cd <PROJECT_DIR>
```

## 1. TODO step name

```powershell
python -u scripts/01_download.py --TODO 2>&1 | Tee-Object logs\01_download.log
```

## 2. TODO step name

```powershell
python -u scripts/02_process.py 2>&1 | Tee-Object logs\02_process.log
```

## Verify

```powershell
pytest tests/ -v
```

Logs go to `logs\<step>_<scope>.log`. Steps that OVERWRITE existing outputs are marked **(overwrites)** in their title.
