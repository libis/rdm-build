# Dataverse Previewers Docker Image

This Docker image bundles file previewers and uploaders for Dataverse.

## Contents

### File Previewers

Based on https://github.com/gdcc/dataverse-previewers - provides in-browser previews for various file types (images, PDFs, text, spreadsheets, GeoJSON, etc.)

### DVWebloader V1

The original vanilla JavaScript file uploader. Located at `/dvwebloader/dvwebloader.html`.

- **Technology**: jQuery + vanilla JavaScript
- **Source**: https://github.com/libis/dvwebloader

### DVWebloader V2

A React-based file uploader that reuses components from `dataverse-frontend`. Located at `/dvwebloader/dvwebloaderV2.html`.

- **Technology**: React 18, TypeScript, Vite
- **Source**: Built from https://github.com/IQSS/dataverse-frontend (`src/standalone-uploader/`)
- **Bundle size**: ~1.5MB (~400KB gzipped)

## DVWebloader URL Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `siteUrl` | Yes | - | The Dataverse installation URL |
| `datasetPid` | Yes | - | The dataset's persistent identifier |
| `key` | Yes | - | User's API token for authentication |
| `dvLocale` | No | `en` | Language locale (e.g., `en`, `de`, `fr`) |

### V2-Only Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `useS3Tagging` | `true` | Set to `false` to disable S3 tagging (for MinIO compatibility) |
| `maxRetries` | `3` | Maximum retries for multipart upload parts |
| `uploadTimeoutMs` | `0` | Upload timeout in ms (`0` = unlimited) |
| `disableMD5Checksum` | `false` | Set to `true` to skip checksum calculation |

## Usage Examples

```
# DVWebloader V1
https://previewers.example.com/dvwebloader/dvwebloader.html?siteUrl=https://dataverse.example.edu&datasetPid=doi:10.5072/FK2/XXXXX&key=your-api-key

# DVWebloader V2
https://previewers.example.com/dvwebloader/dvwebloaderV2.html?siteUrl=https://dataverse.example.edu&datasetPid=doi:10.5072/FK2/XXXXX&key=your-api-key&dvLocale=en

# V2 with S3 tagging disabled (for MinIO)
https://previewers.example.com/dvwebloader/dvwebloaderV2.html?siteUrl=...&datasetPid=...&key=...&useS3Tagging=false
```

## Building

The image is built via the Makefile in the parent directory:

```bash
make build-previewers
```

This will:
1. Clone/update the dataverse-previewers repository
2. Clone/update the dvwebloader repository
3. Build DVWebloader V2 from dataverse-frontend (if available)
4. Build the Docker image
