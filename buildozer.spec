name: Build Kivy APK

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Java 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17

      # --- Android SDK + cmdline-tools ---
      - name: Install Android SDK cmdline-tools
        run: |
          mkdir -p $HOME/android-sdk/cmdline-tools
          cd $HOME/android-sdk/cmdline-tools
          curl -sSLo tools.zip https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
          unzip -q tools.zip -d .
          rm -f tools.zip
          mv cmdline-tools latest
          echo "ANDROID_SDK_ROOT=$HOME/android-sdk" >> $GITHUB_ENV
          echo "$HOME/android-sdk/cmdline-tools/latest/bin" >> $GITHUB_PATH
          echo "$HOME/android-sdk/platform-tools"           >> $GITHUB_PATH
          echo "$HOME/android-sdk/build-tools/33.0.2"       >> $GITHUB_PATH
          yes | $HOME/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
          $HOME/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

      # --- Git richiesto da Buildozer/p4a ---
      - name: Ensure git present
        run: |
          sudo apt-get update
          sudo apt-get install -y git
          git --version

      # --- Dipendenze di sistema utili a Kivy/ReportLab ---
      - name: Install system packages
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            python3 python3-pip python3-setuptools python3-wheel \
            zip unzip libffi-dev libssl-dev libjpeg-dev libfreetype6-dev \
            libgl1-mesa-dev libgles2-mesa-dev libsqlite3-dev zlib1g-dev

      - name: Upgrade pip
        run: /usr/bin/python3 -m pip install --upgrade pip

      # 🔧 Installa Cython in --user e verifica che il binario "cython" sia nel PATH
      - name: Install Cython and verify
        run: |
          /usr/bin/python3 -m pip install --user "Cython==0.29.36"
          echo "$HOME/.local/bin" >> $GITHUB_PATH
          which cython || true
          cython --version

      # Buildozer + deps Python (in --user, così i binari finiscono in ~/.local/bin)
      - name: Install buildozer and python deps
        run: |
          /usr/bin/python3 -m pip install --user buildozer pillow kivy kivymd reportlab

      # --- Build APK (debug) ---
      - name: Build APK (debug)
        env:
          ANDROIDAPI: "33"
          NDKAPI: "21"
          ANDROID_SDK_ROOT: $HOME/android-sdk
          PATH: /usr/bin:/usr/local/bin:$HOME/.local/bin:$HOME/android-sdk/platform-tools:$HOME/android-sdk/cmdline-tools/latest/bin:$HOME/android-sdk/build-tools/33.0.2:$PATH
        run: |
          /usr/bin/python3 -m buildozer -v android debug

      # --- Artifact APK ---
      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: mealapp-apk
          path: bin/*.apk
