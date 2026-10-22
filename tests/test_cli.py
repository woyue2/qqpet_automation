"""测试 CLI 配置加载"""

from src.qq_pet.cli import load_config


def test_load_config_reads_utf8(tmp_path, monkeypatch):
    """配置含中文注释时应按 UTF-8 读取，不受系统 locale 影响"""
    (tmp_path / "config.yaml").write_text(
        'store_path: ""\n# 中文注释\nencryption_key: "aes-256-cbc"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = load_config()

    assert config["store_path"] == ""
    assert config["encryption_key"] == "aes-256-cbc"
