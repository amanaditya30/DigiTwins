import os
import glob
import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
from app.services.rag.vector_store import add_documents_to_store

logger = logging.getLogger(__name__)

# Try to import PDF loaders
try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    PyPDFLoader = None


def create_mock_data() -> List[Document]:
    """Generates mock study notes and interview transcripts for testing out-of-the-box."""
    mock_notes = [
        # DSA Notes
        {
            "content": "Data Structures & Algorithms (DSA): Arrays and strings are fundamental. Two-pointer technique is useful for finding pairs in sorted arrays in O(N) time. Sliding window is great for sub-arrays. Binary search operates in O(log N) time on sorted elements. Graph traversal algorithms include DFS (Depth First Search) using a stack or recursion, and BFS (Breadth First Search) using a queue. Dynamic Programming (DP) optimizes recursive relations by storing subproblem results (memoization/tabulation).",
            "metadata": {"source": "dsa_notes_summary.txt", "category": "DSA"}
        },
        # OS Notes
        {
            "content": "Operating Systems (OS): A deadlock is a state where a set of processes are blocked because each process is holding a resource and waiting for another resource held by some other process. The four necessary conditions for deadlock are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Virtual memory mapping translates logical addresses to physical frames. CPU Scheduling algorithms include Round Robin, Shortest Job First, and First-Come-First-Serve.",
            "metadata": {"source": "os_notes_summary.txt", "category": "Operating Systems"}
        },
        # DBMS Notes
        {
            "content": "Database Management Systems (DBMS): Normalization is the process of organizing data to minimize redundancy. 1NF requires atomicity. 2NF removes partial dependency. 3NF removes transitive dependency. BCNF is a stronger version. Transactions follow ACID properties: Atomicity (all or nothing), Consistency (valid state transitions), Isolation (independent concurrent execution), and Durability (permanent results once committed). Indexes (like B+ trees) speed up read operations but slow down write operations.",
            "metadata": {"source": "dbms_notes_summary.txt", "category": "DBMS"}
        },
        # CN Notes
        {
            "content": "Computer Networks (CN): The OSI model has 7 layers: Physical, Data Link, Network (IP routing), Transport (TCP/UDP reliability), Session, Presentation, and Application. TCP is connection-oriented with 3-way handshake (SYN, SYN-ACK, ACK) and flow control, whereas UDP is connectionless and low-overhead. HTTP is stateless and runs on top of TCP, typically on port 80/443.",
            "metadata": {"source": "cn_notes_summary.txt", "category": "Computer Networks"}
        },
        # Interview Experiences
        {
            "content": "Google Software Engineer Interview Experience: Round 1: DSA (Medium Graph question, BFS layout). Focus on edge cases and big-O complexities. Round 2: DSA (Hard DP, knapsack style). Explain trade-offs between space and time. Round 3: System Design (Designing a rate-limiter, discussion on token bucket vs sliding window log). Round 4: Googliness/Behavioral (conflict resolution, project ownership, learning from failures).",
            "metadata": {"source": "google_interview_exp.txt", "category": "Interview Experience"}
        },
        {
            "content": "Amazon SDE-1 Interview Experience: Focus heavily on Amazon's Leadership Principles (Customer Obsession, Ownership, Bias for Action). DSA rounds focused on Trees and Heaps (e.g., merge K sorted lists). System design was about high-level API design for an e-commerce cart. Ensure you write clean code and dry-run with test inputs.",
            "metadata": {"source": "amazon_interview_exp.txt", "category": "Interview Experience"}
        }
    ]
    
    return [Document(page_content=note["content"], metadata=note["metadata"]) for note in mock_notes]


def ingest_documents_from_directory(dir_path: str = None) -> int:
    """Read files from directory, split, embed, and store in ChromaDB."""
    if not dir_path:
        dir_path = settings.KNOWLEDGE_SOURCES_DIR
        
    os.makedirs(dir_path, exist_ok=True)
    
    documents = []
    
    # Process text files
    txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
    for file_path in txt_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(Document(
                    page_content=content, 
                    metadata={"source": os.path.basename(file_path), "category": "Text Document"}
                ))
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            
    # Process PDF files
    pdf_files = glob.glob(os.path.join(dir_path, "*.pdf"))
    if pdf_files and PyPDFLoader is None:
        logger.warning("PDF files found but PyPDFLoader is not available. Please install pypdf.")
        
    for file_path in pdf_files:
        if PyPDFLoader is not None:
            try:
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                # Attach category metadata
                for page in pages:
                    page.metadata["source"] = os.path.basename(file_path)
                    page.metadata["category"] = "PDF Note"
                documents.extend(pages)
            except Exception as e:
                logger.error(f"Error reading PDF {file_path}: {e}")
                
    # If no documents are found, ingest mock data so the vector database is initialized
    if not documents:
        logger.info("No documents found in knowledge sources directory. Loading default mock data.")
        documents = create_mock_data()
        
    # Text Splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    
    success = add_documents_to_store(chunks)
    if success:
        logger.info(f"Successfully indexed {len(chunks)} chunks into vector database.")
        return len(chunks)
    else:
        logger.error("Failed to index documents into vector database.")
        return 0
