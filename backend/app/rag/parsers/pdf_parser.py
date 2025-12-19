import fitz  # PyMuPDF
import os
from typing import List

# Use the correct import found in your previous steps
from agno.knowledge.document.base import Document

class PDFParser:
    """
    Parses PDF documents and chunks them using a Recursive Character strategy.
    This splits text by hierarchy: Paragraphs (\n\n) -> Lines (\n) -> Sentences (.) -> Words ( ).
    """
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Separators in order of priority (keep paragraphs together if possible)
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def parse(self, file_path: str) -> List[Document]:
        doc = fitz.open(file_path)
        documents = []
        filename = os.path.basename(file_path)

        for page_num, page in enumerate(doc):
            # 1. Extract Text
            # "text" gives a good layout-preserving extraction
            raw_text = page.get_text("text")
            
            # 2. Pre-process (Optional: Clean headers/footers here if needed)
            page_content = raw_text.strip()
            
            if not page_content:
                continue

            # 3. Apply Recursive Chunking
            chunks = self._recursive_split(page_content, self.separators)

            # 4. Create Document Objects
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
        """
        Recursively splits text until chunks fit within chunk_size.
        """
        final_chunks = []
        
        # A. Determine which separator to use
        separator = separators[-1] # Default to empty string (character split)
        new_separators = []
        
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break
        
        # B. Split the text
        splits = text.split(separator) if separator else list(text)
        
        # C. Buffer to build valid chunks
        good_splits = []
        
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                # If a single split is too large, recurse further with finer separators
                if new_separators:
                    good_splits.extend(self._recursive_split(s, new_separators))
                else:
                    # If no separators left, we stick with the large chunk (or force split)
                    good_splits.append(s)
        
        # D. Merge small splits into chunks of correct size with overlap
        return self._merge_splits(good_splits, separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """
        Merges smaller splits into chunks, respecting chunk_size and chunk_overlap.
        """
        docs = []
        current_doc = []
        total_len = 0
        
        for split in splits:
            split_len = len(split)
            
            # Would adding this split exceed chunk size?
            if total_len + split_len + len(separator) > self.chunk_size:
                if current_doc:
                    # 1. Join current buffer into a chunk
                    doc_text = separator.join(current_doc).strip()
                    if doc_text:
                        docs.append(doc_text)
                    
                    # 2. Handle Overlap
                    # Backtrack to keep last segments that fit within overlap limit
                    while total_len > self.chunk_overlap:
                        if not current_doc:
                            break
                        popped = current_doc.pop(0)
                        total_len -= len(popped) + len(separator)
            
            current_doc.append(split)
            total_len += split_len + len(separator)
        
        # Add any remaining text
        if current_doc:
            doc_text = separator.join(current_doc).strip()
            if doc_text:
                docs.append(doc_text)
                
        return docs