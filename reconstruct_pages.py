import json
import re
import sys
import os

def render_node(node):
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float, bool)):
        return str(node)
    if node is None or node is False or node is True:
        return ""
    if isinstance(node, list):
        if len(node) > 0 and node[0] == "$":
            # node is an element: ["$", "tag_name", key, props]
            tag = node[1]
            if not isinstance(tag, str):
                if isinstance(tag, str) and tag.startswith("$L"):
                    # Render children if any
                    if len(node) > 3 and node[3] and "children" in node[3]:
                        return render_node(node[3]["children"])
                    return ""
                if len(node) > 3 and isinstance(node[3], dict) and "children" in node[3]:
                     return render_node(node[3]["children"])
                return ""
            
            # Map Next.js component references to standard tags if we can guess them
            if tag.startswith("$L"):
                props = node[3] if len(node) > 3 else {}
                if "href" in props:
                    tag = "a"
                elif "src" in props:
                    tag = "img"
                else:
                    tag = "div" # fallback
            
            props = node[3] if len(node) > 3 else {}
            if not isinstance(props, dict):
                props = {}
            
            attrs = []
            children = None
            for k, v in props.items():
                if k == "children":
                    children = v
                elif k == "className":
                    attrs.append(f'class="{v}"')
                elif k == "htmlFor":
                    attrs.append(f'for="{v}"')
                elif k == "style":
                    if isinstance(v, dict):
                        style_str = ";".join([f"{sk.replace('Color', '-color').replace('Width', '-width').lower()}:{sv}" for sk, sv in v.items()])
                        attrs.append(f'style="{style_str}"')
                elif k == "dangerouslySetInnerHTML":
                    if isinstance(v, dict) and "__html" in v:
                        children = v["__html"]
                else:
                    if isinstance(v, (str, int, float)):
                        attrs.append(f'{k}="{v}"')
                    elif isinstance(v, bool) and v:
                        if k == "fill" and tag == "img":
                            # fill prop for next/image, usually adds some CSS but we'll ignore or add basic class
                            pass
                        elif k == "priority":
                            pass
                        else:
                            attrs.append(k)

            attr_str = " ".join(attrs)
            attr_part = f" {attr_str}" if attr_str else ""
            
            if tag in ["img", "input", "br", "hr", "meta", "link", "path", "svg"]:
                content = f"<{tag}{attr_part}/>"
                if tag == "svg" and children:
                    content = f"<{tag}{attr_part}>{render_node(children)}</{tag}>"
                return content
            
            content = render_node(children)
            return f"<{tag}{attr_part}>{content}</{tag}>"
        
        return "".join(render_node(child) for child in node)
    
    if isinstance(node, dict):
        if "children" in node:
            return render_node(node["children"])
        out = ""
        for v in node.values():
            out += render_node(v)
        return out

    return ""

def get_main_content_from_txt(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("0:["):
            data = json.loads(line[2:])
            html_content = render_node(data)
            
            # Remove Next.js metadata text and unmapped $L components preceding content
            html_content = re.sub(r'^[^{]*?__PAGE__[^<]*?(?=<)', '', html_content)
            match1 = re.search(r'(<(div|section|nav|h1|h2|h3|p|span|a|img|ul|ol|li))', html_content, flags=re.IGNORECASE)
            if match1:
                html_content = html_content[match1.start():]
                
            # Remove trailing junk ending like </$Ld> etc.
            match2 = re.search(r'(.*</(div|section|nav|h1|h2|h3|p|span|a|ul|ol|li)>)', html_content, flags=re.IGNORECASE | re.DOTALL)
            if match2:
                html_content = match2.group(1)
            
            # Clean up Next.js unmapped markers 
            html_content = re.sub(r'<\/?\$L[a-zA-Z0-9]+[^>]*>', '', html_content)
            
            return html_content
    return ""

def process_file(txt_file, skeleton_file, output_file):
    main_content = get_main_content_from_txt(txt_file)
    if not main_content:
        print(f"Failed to extract content from {txt_file}")
        return False
        
    with open(skeleton_file, 'r', encoding='utf-8') as f:
        skeleton = f.read()
        
    match = re.search(r'(<main[^>]*>)(.*?)(</main>)', skeleton, flags=re.IGNORECASE | re.DOTALL)
    if match:
        new_html = skeleton[:match.start(2)] + main_content + skeleton[match.end(2):]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"Successfully reconstructed {output_file}")
        return True
    else:
        print(f"Could not find <main> in skeleton {skeleton_file}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python reconstruct_pages.py <input_txt> <skeleton_html> <output_html>")
        sys.exit(1)
        
    process_file(sys.argv[1], sys.argv[2], sys.argv[3])
