#!/bin/bash
#
# Dataverse Previewers Initialization Script
# 
# This script runs at container startup to:
# 1. Download and localize external resources (JS, CSS, fonts, images)
# 2. Fix upstream bugs (Bootstrap font URL extraction)
# 3. Apply runtime patches (zip.js forceRangeRequests)
# 4. Copy previewers to nginx webroot
#
# Environment variables:
#   VERSIONS - Comma/space-separated list of previewer versions (default: "v1.5")
#   PREVIEWERS_PROVIDER_URL - Base URL for the previewer installation
#

# Set some defaults as documented
VERSIONS=${VERSIONS:-"v1.5"}

echo "Using Provider Url=${PREVIEWERS_PROVIDER_URL} for versions ${VERSIONS}"
cd /app
# Split VERSIONS on commas and/or spaces and iterate
# Accepts values like: "v1.3,v1.4" or "v1.3 v1.4" or mixed
versions="${VERSIONS//,/ }"

# Install dvwebloader
echo "Installing dvwebloader..."
if [ -d "/app/dvwebloader/src" ]; then
    cd /app/dvwebloader/src
    # Run localinstall.sh from src dir (it expects *.html in cwd)
    bash /app/dvwebloader/localinstall.sh || echo "[WARN] dvwebloader localinstall.sh had issues, continuing..."
    # Copy all built assets to webroot
    mkdir -p /usr/share/nginx/html/dvwebloader
    cp -r ./* /usr/share/nginx/html/dvwebloader/ 2>/dev/null || true
    # Debug: list what was installed
    echo "dvwebloader installed to /usr/share/nginx/html/dvwebloader"
    ls -la /usr/share/nginx/html/dvwebloader/
    ls -la /usr/share/nginx/html/dvwebloader/lib/ 2>/dev/null || echo "[INFO] No lib/ directory created"
else
    echo "[WARN] dvwebloader source not found at /app/dvwebloader/src"
fi

# Install DVWebloader V2 (React-based)
echo "Installing DVWebloader V2..."
if [ -d "/app/dvwebloader-v2/dist" ]; then
    # Copy V2 bundle (from dist/) to webroot alongside V1
    cp -r /app/dvwebloader-v2/dist/* /usr/share/nginx/html/dvwebloader/ 2>/dev/null || true
    echo "DVWebloader V2 installed to /usr/share/nginx/html/dvwebloader"
    ls -la /usr/share/nginx/html/dvwebloader/
else
    echo "[INFO] DVWebloader V2 bundle not found at /app/dvwebloader-v2/dist, skipping"
fi

cd /app
for ver in $versions; do
    # trim surrounding whitespace
    ver="$(echo "$ver" | xargs)"
    [ -z "$ver" ] && continue
    echo "Installing previewers/${ver} from ${PREVIEWERS_PROVIDER_URL}"
    # Patch localinstall.sh to fix the fonturl extraction - ensure it uses bootstrap.min.css not bootstrap-theme.min.css  
    sed -i 's|fonturl=`grep -m 1 https://stackpath.bootstrapcdn.com/ replace_css.sh|fonturl=`grep https://stackpath.bootstrapcdn.com/ replace_css.sh \| grep bootstrap.min.css \| head -1|' ./localinstall.sh
    ./localinstall.sh "previewers/${ver}" "${PREVIEWERS_PROVIDER_URL}"
    
    # Download FontAwesome fonts (not handled by localinstall.sh)
    if [ -f "previewers/${ver}/css/font-awesome.min.css" ]; then
        echo "Downloading FontAwesome fonts..."
        cd "previewers/${ver}/fonts"
        for font in fontawesome-webfont.eot fontawesome-webfont.svg fontawesome-webfont.ttf fontawesome-webfont.woff fontawesome-webfont.woff2; do
            wget --quiet "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/${font}" || echo "Warning: Failed to download ${font}"
        done
        cd /app
    fi
    
    # Download Leaflet images (not handled by localinstall.sh)
    if [ -f "previewers/${ver}/css/leaflet.css" ]; then
        echo "Downloading Leaflet images..."
        mkdir -p "previewers/${ver}/css/images"
        cd "previewers/${ver}/css/images"
        for img in layers.png layers-2x.png marker-icon.png marker-icon-2x.png marker-shadow.png; do
            wget --quiet "https://unpkg.com/leaflet@1.7.1/dist/images/${img}" || echo "Warning: Failed to download ${img}"
        done
        cd /app
    fi
    
    # Download custom fonts referenced in fonts.css (Amiri and Hind Siliguri)
    if [ -f "previewers/${ver}/css/fonts.css" ]; then
        echo "Downloading custom fonts (Amiri, Hind Siliguri)..."
        cd "previewers/${ver}/css"
        # Amiri fonts
        wget --quiet -O Amiri-Regular.woff2 "https://fonts.gstatic.com/s/amiri/v12/J7aRnpd8CGxBHpUutLM.woff2" || echo "Warning: Failed to download Amiri-Regular"
        wget --quiet -O Amiri-Bold.woff2 "https://fonts.gstatic.com/s/amiri/v12/J7acnpd8CGxBHp2VkaY_zp4.woff2" || echo "Warning: Failed to download Amiri-Bold"
        # Hind Siliguri fonts
        wget --quiet -O HindSiliguri-Regular.woff2 "https://fonts.gstatic.com/s/hindsiliguri/v5/ijwTs5juQtsyLLR5jN4cxBEoTJzaxw.woff2" || echo "Warning: Failed to download HindSiliguri-Regular"
        wget --quiet -O HindSiliguri-Bold.woff2 "https://fonts.gstatic.com/s/hindsiliguri/v5/ijwOs5juQtsyLLR5jN4cxBEoRCf_0uYVKw.woff2" || echo "Warning: Failed to download HindSiliguri-Bold"
        cd /app
    fi
    
    # copy any markdown files into the version folder if present (ignore errors)
    cp -- *.md "previewers/${ver}" 2>/dev/null || true
    # ensure the target previewers directory exists and copy only this version to the webroot
    mkdir -p /usr/share/nginx/html/previewers
    cp -r "previewers/${ver}" "/usr/share/nginx/html/previewers/" || echo "Copy failed for ${ver}"
    # Minimal patch: enforce forceRangeRequests in zip.js if present
    zipjs_path="/usr/share/nginx/html/previewers/${ver}/js/zip.js"
    if [ -f "$zipjs_path" ]; then
        sed -i 's|const reader = new zip.ZipReader(new zip.HttpRangeReader(fileUrl));|const reader = new zip.ZipReader(new zip.HttpRangeReader(fileUrl, {forceRangeRequests: true}));|' "$zipjs_path" || true
    fi
done

