#!/usr/bin/env python3
import os, sys, json, argparse, logging, uuid
from pathlib import Path
from typing import Iterable, Optional
import xml.etree.ElementTree as ET

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------- Helpers ----------
def to_text(elem: Optional[ET.Element]) -> str:
    if elem is None:
        return ""
    # preserves inline formatting inside <Answer> using itertext()
    return "".join(elem.itertext()).strip()

def norm_ws(s: str) -> str:
    # collapse awkward whitespace; keep bullets & newlines
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())

def safe_attr(elem: ET.Element, name: str, default: str = "") -> str:
    return elem.get(name, default) if elem is not None else default

def findtext(root: ET.Element, path: str) -> str:
    el = root.find(path)
    return el.text.strip() if (el is not None and el.text) else ""

def iter_xml_files(resources_dir: Path) -> Iterable[Path]:
    for p in resources_dir.rglob("*.xml"):
        yield p

# ---------- Core extraction ----------
def extract_doc_qa_records(xml_path: Path, lang: str = "en") -> Iterable[dict]:
    """
    Yields one JSONL record per QA pair (doc_type='qa') for RAG-friendly ingestion.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logging.warning(f"Skipping {xml_path}: {e}")
        return

    document_id = safe_attr(root, "id", xml_path.stem)
    source = safe_attr(root, "source", "")
    url = safe_attr(root, "url", "")
    focus = findtext(root, "Focus") or ""
    last_reviewed = findtext(root, "LastReviewedDate") or safe_attr(root, "last_reviewed", "")

    qapairs = root.find("QAPairs")
    if qapairs is None:
        return

    for qa in qapairs.findall("QAPair"):
        q_el = qa.find("Question")
        a_el = qa.find("Answer")
        if q_el is None or a_el is None:
            continue

        question = (q_el.text or "").strip()
        answer = norm_ws(to_text(a_el))
        if not answer:
            continue

        qtype = safe_attr(q_el, "qtype", "")
        qid = safe_attr(q_el, "qid", "")
        pid = safe_attr(qa, "pid", "")

        rid = f"{document_id}:{qid or uuid.uuid4().hex}"
        yield {
            "id": rid,
            "doc_type": "qa",
            "document_id": document_id,
            "focus": focus,
            "section": safe_attr(qa, "section", ""),   # if present in XML
            "source": source,
            "url": url,
            "lang": lang,
            "audience": "patient",
            "last_reviewed_date": last_reviewed or None,
            "qtype": qtype,
            "qid": qid,
            "pid": pid,
            # Fields you embed (answer is best; you can also embed question+answer):
            "question": question,
            "answer": answer,
        }

def extract_doc_meta_record(xml_path: Path, lang: str = "en") -> Optional[dict]:
    """
    One metadata record per document (doc_type='doc_meta') for auditing/citation.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logging.warning(f"Skipping meta {xml_path}: {e}")
        return None

    document_id = safe_attr(root, "id", xml_path.stem)
    source = safe_attr(root, "source", "")
    url = safe_attr(root, "url", "")
    focus = findtext(root, "Focus") or ""
    last_reviewed = findtext(root, "LastReviewedDate") or safe_attr(root, "last_reviewed", "")

    return {
        "id": f"{document_id}::meta",
        "doc_type": "doc_meta",
        "document_id": document_id,
        "focus": focus,
        "source": source,
        "url": url,
        "lang": lang,
        "audience": "patient",
        "last_reviewed_date": last_reviewed or None,
    }

# ---------- Writers ----------
def write_jsonl(records: Iterable[dict], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="Extract QA pairs from XML into RAG-ready JSONL.")
    ap.add_argument("--resources", "-r", default="Resources", help="Directory containing XML files")
    ap.add_argument("--out-jsonl", "-o", default="medical_qa.jsonl", help="Output JSONL (QA records)")
    ap.add_argument("--out-meta", "-m", default="medical_docs_meta.jsonl", help="Output JSONL (doc meta)")
    ap.add_argument("--lang", default="en", help="Language tag for the extracted content (e.g., en, hi)")
    args = ap.parse_args()

    resources_dir = Path(args.resources)
    qa_out = Path(args.out_jsonl)
    meta_out = Path(args.out_meta)

    # Stream QA
    def qa_stream():
        for xmlp in iter_xml_files(resources_dir):
            yield from extract_doc_qa_records(xmlp, lang=args.lang)

    # Stream meta
    def meta_stream():
        for xmlp in iter_xml_files(resources_dir):
            rec = extract_doc_meta_record(xmlp, lang=args.lang)
            if rec:
                yield rec

    n_qa = write_jsonl(qa_stream(), qa_out)
    n_meta = write_jsonl(meta_stream(), meta_out)
    logging.info(f"Wrote {n_qa} QA records → {qa_out}")
    logging.info(f"Wrote {n_meta} meta records → {meta_out}")

if __name__ == "__main__":
    main()
