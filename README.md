# HTML to RAG Preprocessor

A lightweight, flexible preprocessing pipeline to convert raw HTML content (from forums, blogs, documentation, etc.) into structured JSONL format for use in Retrieval-Augmented Generation (RAG) pipelines. This tool cleans HTML, extracts useful metadata, splits the content into semantically coherent chunks, and writes it in a machine-readable format.

---

## ✨ Features

* 🧹 **HTML Cleanup**: Removes scripts, styles, boilerplate (headers/footers/navbars), and leaves clean readable text.
* 🏷️ **Metadata Extraction**: Automatically extracts document title, author, date if available.
* 📚 **Chunking**: Uses LangChain's `RecursiveCharacterTextSplitter` to intelligently break content into overlapping chunks for RAG compatibility.
* 📤 **JSONL Output**: Outputs each text chunk and its metadata as a JSON object in a newline-delimited file.
* ✅ **Supports batch input**: Accepts individual files or directories with nested HTML content.

---

## 📦 Requirements

```bash
pip install -r requirements.txt
```

**Dependencies:**

* `beautifulsoup4`
* `langchain_text_splitters`
* `tqdm`

---

## 🚀 Usage

```bash
python preprocess_html.py \
    --input path/to/html_or_folder [additional_paths] \
    --output output.jsonl \
    --chunk_size 1000 \
    --chunk_overlap 200
```

### 🔧 Arguments

| Argument          | Description                                                     |
| ----------------- | --------------------------------------------------------------- |
| `--input` / `-i`  | One or more HTML files or directories to process.               |
| `--output` / `-o` | Path to the output `.jsonl` file. Default: `output.jsonl`       |
| `--chunk_size`    | Max number of characters per chunk. Default: `1000`             |
| `--chunk_overlap` | Number of overlapping characters between chunks. Default: `200` |

---

## 📂 Input Structure

You can pass:

* One or more `.html` or `.htm` files.
* One or more directories (recursively scans for HTML files).

Example directory:

```
data/
├── blog1.html
├── forum/
│   ├── thread1.html
│   └── thread2.html
└── docs/
    └── guide.html
```

Command:

```bash
python preprocess_html.py -i data/ -o chunks.jsonl
```

---

## 📤 Output Format

Each line in the output `.jsonl` file is a JSON object:

```json
{
  "content": "Chunk of cleaned text content...",
  "metadata": {
    "filename": "guide.html",
    "title": "Getting Started Guide",
    "author": "John Doe",
    "date": "2024-05-01T12:00:00Z",
    "chunk": 0
  }
}
```

---

## 🧠 Example Use Case

This script is ideal for preparing a knowledge base from HTML content to feed into:

* 🧠 **RAG pipelines**
* 🔍 **Vector databases** (Chroma, FAISS, Pinecone)
* 💬 **Chatbots with context-aware memory**
* 📚 **Search indexers**

---

## 🛠️ Advanced Tips

* To scrape a website first, use tools like:

  * [`wget --mirror`](https://www.gnu.org/software/wget/manual/html_node/Mirroring.html)
  * [`httrack`](https://www.httrack.com/)
  * Custom scrapers with `requests` + `BeautifulSoup`

* After generating `output.jsonl`, feed it into your embedding + vector store setup.

---

## 📄 License

MIT License
