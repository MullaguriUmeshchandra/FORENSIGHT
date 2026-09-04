#!/usr/bin/env bash
# Exit on any error
set -e

echo "=== [1/2] Installing Backend Dependencies ==="
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== [2/2] Building Frontend Assets ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Build Completed Successfully. Ready for Deployment! ==="
