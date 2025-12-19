import fitz  # PyMuPDF
import os
from typing import List

# Use the correct import for Agno v2
from agno.knowledge.document.base import Document

class PDFParser:
    """
    Parses PDF documents and chunks them using a Recursive Character strategy.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def parse(self, file_path: str) -> List[Document]:
        doc = fitz.open(file_path)
        documents = []
        filename = os.path.basename(file_path)

        for page_num, page in enumerate(doc):
            raw_text = page.get_text("text")
            page_content = raw_text.strip()
            
            if not page_content:
                continue

            chunks = self._recursive_split(page_content, self.separators)

            for i, chunk_text in enumerate(chunks):
                if not chunk_text.strip():
                    continue
                    
                documents.append(
                    Document(
                        content=chunk_text,
                        meta_data={
                            "source": filename,
                            "page": page_num + 1,
                            "chunk_index": i,
                            "file_path": file_path
                        }
                    )
                )
            
        doc.close()
        return documents

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively splits text."""
        final_chunks = []
        separator = separators[-1]
        new_separators = []
        
        for i, sep in enumerate(separators):
            if sep == "": separator = ""; break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break
        
        splits = text.split(separator) if separator else list(text)
        good_splits = []
        
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    good_splits.extend(self._recursive_split(s, new_separators))
                else:
                    good_splits.append(s)
        
        return self._merge_splits(good_splits, separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Merges small splits into chunks."""
        docs = []
        current_doc = []
        total_len = 0
        
        for split in splits:
            split_len = len(split)
            if total_len + split_len + len(separator) > self.chunk_size:
                if current_doc:
                    doc_text = separator.join(current_doc).strip()
                    if doc_text: docs.append(doc_text)
                    while total_len > self.chunk_overlap:
                        if not current_doc: break
                        popped = current_doc.pop(0)
                        total_len -= len(popped) + len(separator)
            current_doc.append(split)
            total_len += split_len + len(separator)
        
        if current_doc:
            doc_text = separator.join(current_doc).strip()
            if doc_text: docs.append(doc_text)
                
        return docs