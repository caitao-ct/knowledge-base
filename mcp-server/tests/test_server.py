import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import safe_join, sha1_text, KnowledgeIndex
from pathlib import Path


class TestSafeJoin:
    def test_normal_path(self, tmp_path):
        base = tmp_path / "docs"
        base.mkdir()
        (base / "test.md").touch()
        result = safe_join(str(base), "test.md")
        assert result == base / "test.md"

    def test_nested_path(self, tmp_path):
        base = tmp_path / "docs"
        base.mkdir()
        subdir = base / "subdir"
        subdir.mkdir()
        (subdir / "test.md").touch()
        result = safe_join(str(base), "subdir/test.md")
        assert result == subdir / "test.md"

    def test_path_traversal_blocked(self, tmp_path):
        base = tmp_path / "docs"
        base.mkdir()
        with pytest.raises(ValueError, match="路径穿越"):
            safe_join(str(base), "../etc/passwd")

    def test_absolute_path_blocked(self, tmp_path):
        base = tmp_path / "docs"
        base.mkdir()
        with pytest.raises(ValueError):
            safe_join(str(base), "/etc/passwd")


class TestSha1Text:
    def test_consistency(self):
        text = "测试文本"
        hash1 = sha1_text(text)
        hash2 = sha1_text(text)
        assert hash1 == hash2
        assert len(hash1) == 40  # SHA1 hex length

    def test_different_texts(self):
        hash1 = sha1_text("text1")
        hash2 = sha1_text("text2")
        assert hash1 != hash2


class TestKnowledgeIndex:
    def test_chunk_markdown_basic(self, tmp_path):
        chroma_dir = tmp_path / ".chroma"
        kb_dir = tmp_path / "docs"
        kb_dir.mkdir()
        indexer = KnowledgeIndex(
            kb_dir=str(kb_dir),
            chroma_dir=str(chroma_dir),
            collection="test",
            embed_model="sentence-transformers"
        )
        text = "## 标题\n内容段落"
        chunks = indexer.chunk_markdown(text, "test.md")
        assert len(chunks) == 1
        assert chunks[0]["title"] == "标题"
        assert chunks[0]["content"] == "## 标题\n内容段落"

    def test_chunk_markdown_multiple_h2(self, tmp_path):
        chroma_dir = tmp_path / ".chroma"
        kb_dir = tmp_path / "docs"
        kb_dir.mkdir()
        indexer = KnowledgeIndex(
            kb_dir=str(kb_dir),
            chroma_dir=str(chroma_dir),
            collection="test",
            embed_model="sentence-transformers"
        )
        text = "## 第一章\n内容1\n\n## 第二章\n内容2"
        chunks = indexer.chunk_markdown(text, "test.md")
        assert len(chunks) == 2
        assert chunks[0]["title"] == "第一章"
        assert chunks[1]["title"] == "第二章"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])