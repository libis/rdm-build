# DVWebloader V2

A standalone React-based file uploader for Dataverse, built as a single JavaScript bundle that can be embedded in external pages.

## Overview

This is a reimplementation of the original DVWebloader using React, leveraging the file upload functionality from the dataverse-frontend project. It provides:

- Drag-and-drop file upload
- Multiple file selection
- Upload progress tracking
- MD5 checksum calculation (optional)
- Direct S3 upload support
- Retry mechanism for failed uploads
- i18n support

## Building

### Prerequisites

This build requires local copies of:
- `dataverse-frontend` at `../../../../dataverse-frontend`
- `dataverse-client-javascript` at `../../../../dataverse-client-javascript` (must be pre-built with `npm run build`)

### Build Commands

```bash
# Install dependencies
npm install

# Build the bundle
npm run build

# Build and copy locales
npm run build:all

# Preview the built bundle
npm run preview
```

### Output

The build produces:
- `dist/dvwebloader-v2.js` - The bundled JavaScript (~1.6MB, ~420KB gzipped)
- `dist/dvwebloader-v2.js.map` - Source map for debugging

## Usage

Include the script in your HTML page:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVWebloader V2</title>
    <script type="module" src="dvwebloader-v2.js"></script>
</head>
<body>
    <div id="root"></div>
</body>
</html>
```

### URL Parameters

The uploader accepts configuration via URL query parameters:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `siteUrl` | Yes | - | The Dataverse installation URL (e.g., `https://demo.dataverse.org`) |
| `datasetPid` | Yes | - | The dataset's persistent identifier (e.g., `doi:10.5072/FK2/ABCDEF`) |
| `key` | Yes | - | User's API token for authentication |
| `dvLocale` | No | `en` | Language locale (e.g., `en`, `de`, `fr`) |
| `useS3Tagging` | No | `true` | Set to `false` to disable S3 tagging (for S3-compatible storage that doesn't support it) |
| `maxRetries` | No | `3` | Maximum number of retries for multipart upload parts |
| `uploadTimeoutMs` | No | `0` | Timeout in milliseconds for file upload operations. `0` = unlimited (recommended for large files) |
| `disableMD5Checksum` | No | `false` | Set to `true` to disable MD5 checksum calculation (faster uploads, less verification) |

### Example URL

```
dvwebloaderV2.html?siteUrl=https://demo.dataverse.org&datasetPid=doi:10.5072/FK2/ABCDEF&key=your-api-token
```

### Example with all options

```
dvwebloaderV2.html?siteUrl=https://demo.dataverse.org&datasetPid=doi:10.5072/FK2/ABCDEF&key=your-api-token&dvLocale=en&useS3Tagging=false&maxRetries=3&uploadTimeoutMs=0&disableMD5Checksum=true
```

## Localization

Place translation files in the `locales/{lang}/` directory. Currently supported:
- `en` - English

The locale can be selected via the `dvLocale` URL parameter.

## Development

To develop the uploader, you can use the Vite dev server:

```bash
npm run dev
```

Note: The dev server requires proper setup of the local source projects.

## Architecture

The bundle includes:
- React 18
- React Bootstrap components
- dataverse-client-javascript (for API communication)
- i18next (for internationalization)
- All CSS is inlined into the JavaScript bundle

## License

See LICENSE file.
