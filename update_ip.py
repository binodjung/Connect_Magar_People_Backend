import socket
import re
import os

def update_flutter_ip():
    # 1. Get the local IP address automatically
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Error detecting IP: {e}")
        return

    # 2. Find the Flutter constants file
    # We check common relative paths
    possible_paths = [
        os.path.join("..", "connect_magar_peoples_frontend", "lib", "core", "constants", "api_constants.dart"),
        os.path.join("connect_magar_peoples_frontend", "lib", "core", "constants", "api_constants.dart"),
        os.path.join("lib", "core", "constants", "api_constants.dart")
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        print("ERROR: Could not find 'api_constants.dart'.")
        print("Make sure you are running this from your project root.")
        return

    # 3. Read and update the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Look for http://xx.xx.xx.xx and replace it with new IP
    new_content = re.sub(r'http://\d+\.\d+\.\d+\.\d+', f'http://{ip}', content)
    
    # 4. Save the changes
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("="*40)
    print(f"SUCCESS: Updated IP to {ip}")
    print(f"FILE: {file_path}")
    print("="*40)
    print("Now hot-restart your Flutter app!")

if __name__ == "__main__":
    update_flutter_ip()
