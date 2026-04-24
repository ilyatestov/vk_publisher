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

### Alternative: Manual release from GitHub UI

If repository automation cannot push tags, run workflow **release** manually:

1. Open **Actions** -> **release** -> **Run workflow**
2. Provide input `tag` (for example: `v2.1.0`)
3. Workflow will build artifacts and create/update GitHub Release for this tag.

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

## 5. (Optional) Publish Docker image to GitHub Packages (GHCR)

Workflow: `.github/workflows/publish-ghcr.yml`

- trigger by tag push `v*` **or** manual Actions run with input `tag`
- publishes image to:
  - `ghcr.io/<owner>/vk_publisher:vX.Y.Z`
  - `ghcr.io/<owner>/vk_publisher:latest`

When you need this:
- yes — if you deploy with Docker/Portainer/Kubernetes and want versioned images
- no — if you only use binary artifacts (`.zip`/`.tar.gz`) or local Python startup
