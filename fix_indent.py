import os
import re
import textwrap

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find st.markdown(f'''...''') or st.markdown('''...''') or st.markdown(\"\"\"...\"\"\")
    pattern = re.compile(r'(st\.markdown\(\s*[f]?)([\"\"\"]{3}|\'\'\'{3})(.*?)\2', re.DOTALL)
    
    def replacer(match):
        prefix = match.group(1)
        quote = match.group(2)
        text = match.group(3)
        dedented_text = textwrap.dedent(text)
        return prefix + quote + dedented_text + quote

    new_content = pattern.sub(replacer, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {filepath}')

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py') and file != 'fix_indent.py':
            process_file(os.path.join(root, file))
