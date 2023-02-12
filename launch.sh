#!/bin/bash

pyinstaller --onefile -w StatusBoard.py
mv dist/StatusBoard.exe StatusBoard.exe

git add .
git commit -m "updated .exe file"
git push origin main