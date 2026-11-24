# Run from source
run:
    uv run src/tinyshot.py

# Build the executable locally
build:
    uv run pyinstaller --noconfirm --onedir --windowed \
      --exclude-module PyQt6.QtWebEngineCore \
      --exclude-module PyQt6.QtMultimedia \
      --exclude-module PyQt6.QtQml \
      --exclude-module PyQt6.QtQuick \
      --exclude-module PyQt6.Qt3D \
      --exclude-module PyQt6.QtSql \
      --exclude-module PyQt6.QtNetwork \
      --exclude-module PyQt6.QtPdf \
      src/tinyshot.py

# Clean build artifacts
clean:
    rm -rf build dist
