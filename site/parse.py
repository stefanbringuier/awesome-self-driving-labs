import os
import re
import shutil

def parse_readme(readme_path, output_dir, bibtex_filename='../bibtex/references.bib', conduct_filename='../code-of-conduct.md'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    assets_dir = os.path.join(output_dir, 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # Copying bibtex and code of conduct files to assets directory
    shutil.copy(bibtex_filename, os.path.join(assets_dir, 'references.bib'))
    shutil.copy(conduct_filename, assets_dir)

    with open(readme_path, 'r') as file:
        content = file.readlines()

    nav_entries = []
    index_content = []
    section_content = []
    current_title = ''
    skip_list_items = False

    for line in content:
        if 'bibtex/references.bib' in line:
            line = line.replace('bibtex/references.bib', 'assets/references.bib')

        # Logic to skip content list (not working)
        if line.startswith('## ') and line.strip() == '## Contents':
            skip_list_items = True
            continue 
        elif skip_list_items and (line.strip().startswith('- ') or line.strip().startswith('* ')):
            continue 
        elif skip_list_items and line.strip() == '':
            continue  
        else:
            skip_list_items = False  

        if line.startswith('# ') and not current_title: 
            index_content.append(line + "\n")
        elif line.startswith('## '): 
            if current_title:
                write_section_to_file(current_title, section_content, output_dir, nav_entries, assets_dir, readme_path)
            current_title = line.strip("# ").strip()
            section_content = [line + "\n"]  
        else:
            section_content.append(handle_local_references(line, assets_dir, readme_path) + "\n")

    if current_title:
        write_section_to_file(current_title, section_content, output_dir, nav_entries, assets_dir, readme_path)

    # Write index_content to index.md
    index_path = os.path.join(output_dir, 'index.md')
    with open(index_path, 'w') as file:
        file.writelines(index_content)
    nav_entries.insert(0, {'title': 'Home', 'file': 'index.md'})

    return nav_entries

def handle_local_references(line, assets_dir, readme_path):
    pattern = r'\[.*?\]\((.*?)\)'
    matches = re.findall(pattern, line)
    readme_dir = os.path.dirname(readme_path)

    for match in matches:
        if not match.startswith(('http://', 'https://', 'mailto:')):
            local_path = os.path.join(readme_dir, match)
            if os.path.isfile(local_path):
                dest_path = os.path.join(assets_dir, os.path.basename(match))
                shutil.copy(local_path, dest_path)
                new_path = os.path.join('assets', os.path.basename(match))
                line = line.replace(match, new_path)
            else:
                print(f"Skipping directory or invalid path: {local_path}")
    return line

def write_section_to_file(title, content, output_dir, nav_entries, assets_dir, readme_path):
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
