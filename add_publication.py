#!/usr/bin/env python3
"""
Script to convert BibTeX entries to publications.json format.

Accepts one or more BibTeX entries; entries may be separated by whitespace,
commas, or no separator at all. Each entry is reviewed interactively.

Usage: python add_publication.py [bibtex-file.bib] or pipe BibTeX via stdin
"""

import json
import re
import sys
from typing import Dict, List, Any, Optional


def split_bibtex_entries(text: str) -> List[str]:
    """Split a BibTeX document into individual entries using brace matching.

    Handles entries separated by whitespace, commas, or no separator at all.
    """
    entries = []
    i = 0
    n = len(text)
    while i < n:
        at_pos = text.find('@', i)
        if at_pos == -1:
            break
        brace_pos = text.find('{', at_pos)
        if brace_pos == -1:
            break
        depth = 1
        j = brace_pos + 1
        while j < n and depth > 0:
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        if depth == 0:
            entries.append(text[at_pos:j])
            i = j
        else:
            # Malformed (unbalanced braces) — stop to avoid infinite loop
            break
    return entries


def parse_bibtex(bibtex: str) -> Dict[str, Any]:
    """Parse a single BibTeX entry into a dictionary."""
    entry = {}

    # Extract entry type
    type_match = re.search(r'@(\w+)\s*\{', bibtex, re.IGNORECASE)
    if type_match:
        entry['entrytype'] = type_match.group(1).lower()

    # Extract fields - handle both {value} and "value" formats
    field_pattern = r'(\w+)\s*=\s*[\{"]([^}"]*)[\}]"?,?'
    for match in re.finditer(field_pattern, bibtex, re.IGNORECASE | re.DOTALL):
        key = match.group(1).lower()
        value = match.group(2).strip()
        # Remove LaTeX commands and braces
        value = re.sub(r'\\[a-z]+\{([^}]*)\}', r'\1', value)
        value = value.replace('{', '').replace('}', '')
        # Handle special LaTeX characters
        value = value.replace('\\&', '&').replace('\\%', '%')
        value = value.replace('\\$', '$').replace('\\#', '#')
        entry[key] = value

    return entry


def bibtex_to_publication(bibtex_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a parsed BibTeX entry to publications.json format."""
    pub = {
        "title": bibtex_entry.get("title", ""),
        "authors": [],
        "venue": {
            "name": "",
            "url": ""
        },
        "paper": "",
        "video": "",
        "year": bibtex_entry.get("year", ""),
        "featured": False,
        "type": "Paper",
        "topic": "LAN",
        "blogPost": "",
        "code": "",
        "software": "",
        "media": []
    }
    
    # Parse authors
    if "author" in bibtex_entry:
        authors_str = bibtex_entry["author"]
        # Split by "and" (case insensitive)
        authors = re.split(r'\s+and\s+', authors_str, flags=re.IGNORECASE)
        
        for author in authors:
            author = author.strip()
            # Handle "Last, First" format
            if ',' in author:
                parts = [p.strip() for p in author.split(',')]
                if len(parts) >= 2:
                    author = f"{parts[1]} {parts[0]}".strip()
            # Add as string (not object) since author info comes from authors.json
            pub["authors"].append(author)
    
    # Map venue based on entry type
    entry_type = bibtex_entry.get("entrytype", "article")
    if entry_type in ["inproceedings", "conference"]:
        pub["venue"]["name"] = bibtex_entry.get("booktitle") or bibtex_entry.get("journal") or ""
        pub["type"] = "Paper"
    elif entry_type == "article":
        pub["venue"]["name"] = bibtex_entry.get("journal") or bibtex_entry.get("booktitle") or ""
        pub["type"] = "Paper"
    elif entry_type in ["phdthesis", "mastersthesis"]:
        pub["venue"]["name"] = "Ph.D. Dissertation"
        pub["type"] = "Paper"
    else:
        pub["venue"]["name"] = bibtex_entry.get("booktitle") or bibtex_entry.get("journal") or ""
    
    # Extract paper URL from various fields
    if "url" in bibtex_entry:
        pub["paper"] = bibtex_entry["url"]
    elif "eprint" in bibtex_entry:
        archive_prefix = bibtex_entry.get("archiveprefix", "").lower()
        if archive_prefix == "arxiv":
            eprint = bibtex_entry["eprint"]
            pub["paper"] = f"https://arxiv.org/abs/{eprint}"
            pub["venue"]["url"] = pub["paper"]
    
    # Extract DOI and use as paper URL if paper URL not already set
    if "doi" in bibtex_entry and not pub["paper"]:
        doi = bibtex_entry["doi"]
        # Remove "https://doi.org/" if present
        doi = re.sub(r'^https?://doi\.org/', '', doi)
        pub["paper"] = f"https://doi.org/{doi}"
    
    return pub


def customize_publication(pub: Dict[str, Any]) -> Dict[str, Any]:
    """Interactively customize publication fields."""
    print('\n=== Customize Publication ===\n')
    print('Current values:')
    print(json.dumps(pub, indent=2))
    print('\n')
    
    # Helper function for prompts
    def prompt(field_name: str, current_value: Any, field_type: type = str) -> Any:
        if isinstance(current_value, bool):
            prompt_text = f"{field_name} (y/n) [{'y' if current_value else 'n'}]: "
        else:
            prompt_text = f"{field_name} [{current_value}]: "
        
        response = input(prompt_text).strip()
        if not response:
            return current_value
        
        if field_type == bool:
            return response.lower() == 'y'
        elif field_type == int:
            try:
                return int(response)
            except ValueError:
                return current_value
        else:
            return response
    
    # Title
    pub["title"] = prompt("Title", pub["title"])
    
    # Authors
    # Handle both string and object formats
    authors_str = ", ".join([
        (a if isinstance(a, str) else a["name"]) + 
        ("*" if (isinstance(a, dict) and a.get("equalContribution")) else "") 
        for a in pub["authors"]
    ])
    print(f"\nCurrent authors: {authors_str}")
    authors_input = prompt("Authors (comma-separated, use * for equal contribution, e.g., 'John Doe*, Jane Smith*')", "", str)
    if authors_input:
        authors = []
        for author in authors_input.split(','):
            author = author.strip()
            has_asterisk = author.endswith('*')
            name = author[:-1].strip() if has_asterisk else author
            if has_asterisk:
                # Use object format for equal contribution
                authors.append({"name": name, "equalContribution": True})
            else:
                # Use string format for simple authors
                authors.append(name)
        pub["authors"] = authors
    
    # Venue
    pub["venue"]["name"] = prompt("Venue name", pub["venue"]["name"])
    pub["venue"]["url"] = prompt("Venue URL", pub["venue"]["url"])
    
    # URLs
    pub["paper"] = prompt("Paper URL", pub["paper"])
    pub["video"] = prompt("Video URL", pub["video"])
    pub["blogPost"] = prompt("Blog Post URL", pub["blogPost"])
    pub["code"] = prompt("Code URL", pub["code"])
    pub["software"] = prompt("Software URL", pub["software"])
    
    # Media links (custom media with name and URL)
    print("\nMedia links (custom media entries with name and URL):")
    print("Enter media entries in format: 'Name:URL' (e.g., 'Demo:https://example.com/demo')")
    print("Press Enter with empty input to finish adding media")
    media_list = []
    while True:
        media_input = prompt("Media (Name:URL or press Enter to finish)", "")
        if not media_input:
            break
        if ':' in media_input:
            parts = media_input.split(':', 1)
            media_list.append({"name": parts[0].strip(), "url": parts[1].strip()})
        else:
            print("  Warning: Format should be 'Name:URL', skipping this entry")
    pub["media"] = media_list
    
    # Metadata
    pub["year"] = prompt("Year", pub["year"], int) if isinstance(pub["year"], (int, str)) else prompt("Year", str(pub["year"]))
    pub["type"] = prompt("Type (Paper/Poster/Demo/Short Paper/Book Chapter)", pub["type"])
    pub["topic"] = prompt("Topic (LAN/AI4SS/INFO/SV)", pub["topic"])
    pub["featured"] = prompt("Featured?", pub["featured"], bool)
    
    # Optional fields
    award = prompt("Award (leave empty if none)", "")
    if award:
        pub["award"] = award
    
    return pub


def update_authors_json(new_pubs: List[Dict[str, Any]],
                        authors_path: str = 'assets/authors.json') -> None:
    """Add any new authors from new_pubs to authors.json, prompting for URL/extraClass."""
    with open(authors_path, 'r', encoding='utf-8') as f:
        authors = json.load(f)

    seen_names = set()
    for pub in new_pubs:
        for a in pub.get('authors', []):
            name = a if isinstance(a, str) else a.get('name', '')
            if name:
                seen_names.add(name)

    new_names = sorted(seen_names - set(authors.keys()))
    if not new_names:
        print('\nNo new authors to add to authors.json.')
        return

    print(f'\n=== {len(new_names)} new author(s) for authors.json ===')
    print('Press Enter to skip a field. Use extraClass "isle" for advisees.\n')

    for name in new_names:
        print(f'Author: {name}')
        url = input('  URL (optional): ').strip()
        extra_class = input('  extraClass (optional): ').strip()
        entry: Dict[str, Any] = {}
        if url:
            entry['url'] = url
        if extra_class:
            entry['extraClass'] = extra_class
        authors[name] = entry

    with open(authors_path, 'w', encoding='utf-8') as f:
        json.dump(authors, f, indent=2, ensure_ascii=False)
    print(f'\n✓ {len(new_names)} author(s) added to {authors_path}')


def main():
    """Main function."""
    bibtex = ""

    # Read from file or stdin
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            bibtex = f.read()
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("Paste your BibTeX entries below (press Ctrl+D when done, or Ctrl+Z on Windows):\n")
        bibtex = sys.stdin.read()

    if not bibtex.strip():
        print("Error: No BibTeX input provided", file=sys.stderr)
        print("Usage: python add_publication.py [bibtex-file.bib]", file=sys.stderr)
        print("   or: echo '@article{...}' | python add_publication.py", file=sys.stderr)
        sys.exit(1)

    # Split into individual entries
    entries = split_bibtex_entries(bibtex)
    if not entries:
        print("Error: No BibTeX entries found in input", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(entries)} BibTeX entry(ies).\n")

    new_pubs: List[Dict[str, Any]] = []
    for idx, entry_text in enumerate(entries, 1):
        print(f"\n========== Entry {idx} of {len(entries)} ==========")
        bibtex_entry = parse_bibtex(entry_text)
        print("Parsed BibTeX entry:")
        print(json.dumps(bibtex_entry, indent=2))

        action = input("\nCustomize and add this entry? (y/n/q) [y]: ").strip().lower()
        if action == 'q':
            print("Stopping; remaining entries skipped.")
            break
        if action == 'n':
            print("Skipped.")
            continue

        pub = bibtex_to_publication(bibtex_entry)
        pub = customize_publication(pub)

        print('\n=== Final Publication Entry ===\n')
        print(json.dumps(pub, indent=2))

        new_pubs.append(pub)

    if not new_pubs:
        print('\nNo publications to add.')
        return

    print(f'\n========== {len(new_pubs)} publication(s) ready ==========')
    append = input(f'\nAppend all {len(new_pubs)} to assets/publications.json? (y/n): ').strip().lower()

    if append == 'y':
        with open('assets/publications.json', 'r', encoding='utf-8') as f:
            pubs = json.load(f)
        # Insert at beginning, preserving the order from the input file
        pubs[0:0] = new_pubs
        with open('assets/publications.json', 'w', encoding='utf-8') as f:
            json.dump(pubs, f, indent=2, ensure_ascii=False)
        print(f'\n✓ {len(new_pubs)} publication(s) added to assets/publications.json')

        # Keep authors.json in sync: every author in publications.json must
        # have a profile entry, otherwise the site can't enrich their name.
        update_authors_json(new_pubs)
    else:
        print('\nCopy the JSON(s) above and add them manually to assets/publications.json')


if __name__ == "__main__":
    main()



