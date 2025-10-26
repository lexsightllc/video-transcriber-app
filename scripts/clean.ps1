. "$PSScriptRoot/Utils.ps1"

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$ProjectRoot/build"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$ProjectRoot/dist"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$ProjectRoot/htmlcov"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$ProjectRoot/.pytest_cache"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$ProjectRoot/.mypy_cache"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$ProjectRoot/.ruff_cache"
Remove-Item -Force -ErrorAction SilentlyContinue "$ProjectRoot/coverage.xml"
Get-ChildItem -Path $ProjectRoot -Recurse -Include *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $ProjectRoot -Recurse -Include __pycache__ | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
