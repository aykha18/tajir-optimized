import os

def remove_admin_code():
    file_path = 'app.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    
    start_marker = "# Admin authentication decorator"
    end_marker = "@app.route('/static/<path:filename>')"
    
    for line in lines:
        if start_marker in line:
            skip = True
            print(f"Skipping started at line: {line.strip()}")
        
        if end_marker in line:
            skip = False
            print(f"Skipping ended at line: {line.strip()}")
        
        if not skip:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Cleanup completed.")

if __name__ == "__main__":
    remove_admin_code()
