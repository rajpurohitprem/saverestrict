#!/data/data/com.termux/files/usr/bin/bash

echo "📦 Updating Termux packages..."
pkg update -y
pkg upgrade -y

echo "📦 Installing system dependencies..."
pkg install -y clang python libffi openssl rust

echo "🐍 Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

echo "📦 Installing Python dependencies..."
pip install aiohttp==3.8.5
pip install aiogram==2.25.1
pip install telethon tqdm

echo
echo "✅ All dependencies installed successfully!"
echo "📄 Verifying package versions:"

echo -n "telethon: "
pip show telethon | grep Version

echo -n "aiogram: "
pip show aiogram | grep Version

echo -n "aiohttp: "
pip show aiohttp | grep Version

echo -n "tqdm: "
pip show tqdm | grep Version

echo
echo "✅ Environment is ready! You can now run your bot."
