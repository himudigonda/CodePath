import os
from pathlib import Path

README_PATH = "README.md"
BASE_DIR = Path(__file__).parent


def find_notebooks():
    """
    Find all notebooks in the expected structure:
    - Each Unit has 2 Sessions
    - Each Session has 4 notebooks (Standard1, Standard2, Advanced1, Advanced2)
    """
    notebooks_data = {}

    # Get all unit directories
    unit_dirs = [
        d
        for d in BASE_DIR.iterdir()
        if d.is_dir() and d.name.lower().startswith("unit")
    ]

    for unit_dir in sorted(unit_dirs, key=lambda x: x.name):
        unit_name = unit_dir.name
        notebooks_data[unit_name] = {}

        # Get all session directories
        session_dirs = [
            d
            for d in unit_dir.iterdir()
            if d.is_dir() and d.name.lower().startswith("session")
        ]

        for session_dir in sorted(session_dirs, key=lambda x: x.name):
            session_name = session_dir.name
            notebooks_data[unit_name][session_name] = []

            # Get all notebook files
            notebook_files = [
                f for f in session_dir.iterdir() if f.is_file() and f.suffix == ".ipynb"
            ]

            for notebook_file in sorted(notebook_files, key=lambda x: x.name):
                rel_path = f"{unit_name}/{session_name}/{notebook_file.name}"
                notebooks_data[unit_name][session_name].append(
                    {"name": notebook_file.name, "path": rel_path.replace(" ", "%20")}
                )

    return notebooks_data


def build_toc_and_unit_sections(notebooks_data):
    """
    Build a Table of Contents and per-unit tables.
    - TOC links to each unit section anchor
    - Each unit section contains a table: Session | Notebook | Link
    """
    toc_lines = []
    section_blocks = []

    for unit_name in sorted(notebooks_data.keys()):
        anchor = unit_name.lower().replace(" ", "-")
        toc_lines.append(f"- [{unit_name}](#{anchor})")

        rows = [
            f"### {unit_name}",
            "",
            "| Session | Notebook | Link |",
            "|---------|----------|------|",
        ]

        unit_sessions = notebooks_data[unit_name]
        for session_name in sorted(unit_sessions.keys()):
            session_notebooks = unit_sessions[session_name]

            if not session_notebooks:
                rows.append(f"| {session_name} | *No notebooks yet* | |")
                continue

            for notebook in session_notebooks:
                rows.append(
                    f"| {session_name} | {notebook['name']} | "
                    f"[{notebook['name']}]({notebook['path']}) |"
                )

        section_blocks.append("\n".join(rows))

    toc_md = "\n".join(toc_lines)
    sections_md = "\n\n".join(section_blocks)
    return toc_md, sections_md


def update_readme_from_data(notebooks_data):
    """
    Update the README.md file with a TOC and per-unit tables
    """
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the table section
        start_marker = "## Table of Contents"
        end_marker = "\n*This table is automatically updated by"

        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)

        if start_idx == -1 or end_idx == -1:
            print("Could not find table section markers in README.md")
            return False

        # Build TOC and sections
        toc_md, sections_md = build_toc_and_unit_sections(notebooks_data)

        # Create new content block
        new_table_content = (
            "## Table of Contents\n\n" + toc_md + "\n\n" + sections_md + "\n"
        )

        # Reconstruct the file content
        before_table = content[:start_idx]
        after_table = content[end_idx:]

        new_content = before_table + new_table_content + after_table

        # Write back to file
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ README.md updated successfully with TOC and per-unit tables!")
        return True

    except Exception as e:
        print(f"❌ Error updating README.md: {e}")
        return False


def print_structure_summary(notebooks_data):
    """
    Print a summary of the current structure
    """
    print("\n📁 Current Structure:")
    print("=" * 50)

    total_notebooks = 0
    for unit_name in sorted(notebooks_data.keys()):
        print(f"\n{unit_name}:")
        unit_notebooks = 0

        for session_name in sorted(notebooks_data[unit_name].keys()):
            session_notebooks = notebooks_data[unit_name][session_name]
            notebook_count = len(session_notebooks)
            unit_notebooks += notebook_count

            print(f"  └── {session_name}: {notebook_count} notebooks")
            for notebook in session_notebooks:
                print(f"      └── {notebook['name']}")

        print(f"  Total: {unit_notebooks} notebooks")
        total_notebooks += unit_notebooks

    print(f"\n📊 Overall: {len(notebooks_data)} units, {total_notebooks} notebooks")
    print("=" * 50)


if __name__ == "__main__":
    print("🔄 Updating README table...")

    # Find all notebooks
    notebooks_data = find_notebooks()

    # Print structure summary
    print_structure_summary(notebooks_data)

    # Update README with new structure
    success = update_readme_from_data(notebooks_data)

    if success:
        print("\n🎉 Update completed successfully!")
    else:
        print("\n💥 Update failed!")
