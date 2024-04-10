import os
import shutil

def parse_readme(readme_path, output_dir, bibtex_filename='references.bib'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ensure the assets directory exists
    assets_dir = os.path.join(output_dir, 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Copy the BibTeX file to the assets directory
    shutil.copy(bibtex_filename, assets_dir)

    with open(readme_path, 'r') as file:
        content = file.readlines()

    nav_entries = []
    index_content = []
    section_content = []
    current_title = ''
    for line in content:
        if "<!--omit_from_toc_-->" in line:
            line = line.replace("<!--omit_from_toc_-->", "").strip()
        if line.startswith('# ') and not current_title:
            index_content.append(line)
        elif line.startswith('## '):
            if current_title:
                write_section_to_file(current_title, section_content, output_dir, nav_entries)
                section_content = []
            current_title = line.strip()[3:].strip()
            section_content.append(f"## {current_title}\n")
        else:
            if '[references.bib]' in line:  # Adjust link to BibTeX file
                line = line.replace('[references.bib]', '(assets/references.bib)')
            if current_title:
                section_content.append(line)
            else:
                index_content.append(line)

    if current_title:
        write_section_to_file(current_title, section_content, output_dir, nav_entries)

    index_path = os.path.join(output_dir, 'index.md')
    with open(index_path, 'w') as file:
        file.writelines(index_content)
    nav_entries.insert(0, {'title': 'Home', 'file': 'index.md'})

    return nav_entries


def write_section_to_file(title, content, output_dir, nav_entries):
    filename = f"{title.replace(' ', '_').lower()}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as file:
        file.writelines(content)
    nav_entries.append({'title': title, 'file': filename})

def update_mkdocs_nav(nav_entries, mkdocs_yml_path='mkdocs.yml'):
    nav_lines = ['nav:']
    for entry in nav_entries:
        nav_lines.append(f"  - {entry['title']}: {entry['file']}")

    with open(mkdocs_yml_path, 'r') as file:
        lines = file.readlines()

    with open(mkdocs_yml_path, 'w') as file:
        in_nav = False
        for line in lines:
            if line.strip() == 'nav:':
                in_nav = True
                file.writelines('\n'.join(nav_lines) + '\n')
            elif in_nav and line.startswith('  -'):
                continue
            else:
                in_nav = False
                file.write(line)

if "__main__" == __name__:
    readme_path = '../readme.md'
    output_dir = 'docs'
    nav_entries = parse_readme(readme_path, output_dir)
    update_mkdocs_nav(nav_entries)
