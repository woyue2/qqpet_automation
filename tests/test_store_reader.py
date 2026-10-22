"""测试 electron-store 读写"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.qq_pet import store_reader
from src.qq_pet.store_reader import find_store_path, read_store, write_store


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def test_write_and_read_encrypted(temp_dir):
    """测试加密写入和读取"""
    path = temp_dir / "config.json"
    data = {
        "pet": {
            "info": {"name": "小Q", "hunger": 2500, "clean": 3000, "health": 5, "mood": 800},
            "maxInfo": {"level": 10, "hunger": 4000, "clean": 4000, "health": 5, "mood": 1000},
        }
    }
    write_store(path, data, encryption_key="aes-256-cbc")
    assert path.exists()

    # 验证文件是加密的（第17字节是 ':'）
    raw = path.read_bytes()
    assert len(raw) > 17
    assert raw[16:17] == b":"

    # 读取并验证
    result = read_store(path, encryption_key="aes-256-cbc")
    assert result["pet"]["info"]["name"] == "小Q"
    assert result["pet"]["info"]["hunger"] == 2500


def test_write_and_read_unencrypted(temp_dir):
    """测试明文写入和读取"""
    path = temp_dir / "configDev.json"
    data = {"pet": {"info": {"name": "测试宠物"}}}
    write_store(path, data, encryption_key="")
    result = read_store(path, encryption_key="")
    assert result["pet"]["info"]["name"] == "测试宠物"


def test_read_nonexistent_raises(temp_dir):
    """读取不存在的文件应该报错"""
    with pytest.raises(FileNotFoundError):
        read_store(temp_dir / "nonexistent.json")


def test_find_store_path_custom_path_used(temp_dir):
    """指定了 custom_path 时应直接使用"""
    path = temp_dir / "custom" / "config.json"
    path.parent.mkdir()
    path.write_text("{}", encoding="utf-8")
    assert find_store_path(str(path)) == path


def test_find_store_path_custom_path_missing_raises(temp_dir):
    """指定了不存在的 custom_path 时应报错，而不是回退自动检测"""
    with pytest.raises(FileNotFoundError, match="指定的数据文件不存在"):
        find_store_path(str(temp_dir / "missing.json"))


def test_find_store_path_windows_ported_app(monkeypatch, temp_dir):
    """Windows 下应自动发现移植版写出的 config-macos.json"""
    store = temp_dir / "qq-pet-macos" / "config-macos.json"
    store.parent.mkdir()
    store.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(store_reader.platform, "system", lambda: "Windows")
    monkeypatch.setenv("APPDATA", str(temp_dir))

    assert find_store_path() == store


def test_find_store_path_windows_original_app(monkeypatch, temp_dir):
    """Windows 原版数据文件仍能被自动发现"""
    store = temp_dir / "pet" / "config.json"
    store.parent.mkdir()
    store.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(store_reader.platform, "system", lambda: "Windows")
    monkeypatch.setenv("APPDATA", str(temp_dir))

    assert find_store_path() == store
