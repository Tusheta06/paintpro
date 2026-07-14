import os
import re
import textwrap

def fix_html_indentation(directory):
    count = 0
    # Match f"""...""", """...""", f'''...''', '''...'''
    pattern = re.compile(r'([fF]?)([\"\"\"]{3}|\'\'\'{3})(.*?)\2', re.DOTALL)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'): continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            def replacer(match):
                prefix = match.group(1)
                quote = match.group(2)
                text = match.group(3)
                
                # Only dedent if it contains basic HTML tags (this avoids dedenting raw text/SQL)
                if re.search(r'<\/?(?:div|span|tr|td|th|table|b|i|small|a|button)', text, re.IGNORECASE):
                    # Remove common leading whitespace
                    dedented_text = textwrap.dedent(text)
                    # For safety, ensure it doesn't start with any spaces on the first line after a newline
                    # Actually, textwrap.dedent does exactly what we need
                    return prefix + quote + dedented_text + quote
                    
                return match.group(0)
                
            new_content = pattern.sub(replacer, content)
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                print(f"Fixed {path}")
                
    print(f"Total files fixed in {directory}: {count}")

fix_html_indentation('views')
fix_html_indentation('components')
if os.path.exists('app.py'):
    fix_html_indentation('.')
