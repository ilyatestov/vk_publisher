# Release process (GitHub + Windows/Linux bundles)

## 1. Prepare release

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest -q
pip-audit -r requirements.txt
```

## 2. Create and push tag

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

After tag push (`v*`) workflow `.github/workflows/release.yml` builds:

- `vk_publisher-vX.Y.Z-linux.tar.gz`
- `vk_publisher-vX.Y.Z-windows.zip`
- SHA256 checksum files for each archive

## 3. Local build scripts

### Linux

```bash
bash scripts/release/build_linux.sh vX.Y.Z
```

### Windows (PowerShell)

```powershell
./scripts/release/build_windows.ps1 -Tag vX.Y.Z
```

## 4. Verify archive integrity

### Linux/macOS

```bash
sha256sum -c vk_publisher-vX.Y.Z-linux.tar.gz.sha256
```

### Windows

```powershell
Get-FileHash -Algorithm SHA256 .\vk_publisher-vX.Y.Z-windows.zip
```
