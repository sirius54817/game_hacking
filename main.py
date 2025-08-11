from models.file_manager import FileManager
from models.user_manager import UserManager
import os
from network.transfer_manager import TransferManager
import threading
import asyncio
import time

def start_transfer_server(transfer_manager):
    """Start WiFi server in a separate thread"""
    wifi_thread = threading.Thread(
        target=transfer_manager.start_wifi_server,
        daemon=True
    )
    wifi_thread.start()

async def start_bluetooth_server(transfer_manager):
    """Start Bluetooth server"""
    await transfer_manager.start_bluetooth_server()

async def main():
    # Initialize managers
    storage_path = "secure_storage"
    users_db_path = "users.db"
    
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
        
    file_manager = FileManager(storage_path)
    user_manager = UserManager(users_db_path)

    # Create a test user
    user = user_manager.create_user("testuser", "password123")

    # Initialize transfer manager
    transfer_manager = TransferManager(file_manager)
    
    # Get local IP address
    local_ip = transfer_manager.get_local_ip()
    print(f"Local IP address: {local_ip}")
    
    # Start transfer servers
    start_transfer_server(transfer_manager)
    bluetooth_task = asyncio.create_task(start_bluetooth_server(transfer_manager))

    # Example: Encrypt and save a file
    file_path = "example.txt"
    with open(file_path, "w") as f:
        f.write("This is a secret message!")

    metadata = file_manager.save_encrypted_file(
        file_path=file_path,
        password="file_password",
        user_id=user['user_id']
    )

    print("\nFile Transfer Options:")
    print("1. Send file via WiFi")
    print("2. Send file via Bluetooth")
    print("3. Wait to receive file")
    print("4. Exit")

    while True:
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            target_ip = input("Enter target IP address: ")
            try:
                print(f"Sending file to {target_ip}...")
                transfer_manager.send_file_wifi(
                    metadata,
                    target_host=target_ip,
                    target_port=5000
                )
            except Exception as e:
                print(f"Error sending file: {e}")
                
        elif choice == "2":
            print("Scanning for Bluetooth devices...")
            devices = await transfer_manager.discover_bluetooth_devices()
            if devices:
                print("\nAvailable devices:")
                for i, (addr, name, _) in enumerate(devices, 1):
                    print(f"{i}. {name} ({addr})")
                device_choice = input("\nSelect device number: ")
                try:
                    device_idx = int(device_choice) - 1
                    if 0 <= device_idx < len(devices):
                        print(f"Sending file to {devices[device_idx][1]}...")
                        await transfer_manager.send_file_bluetooth(
                            metadata,
                            devices[device_idx][0]
                        )
                    else:
                        print("Invalid device selection")
                except ValueError:
                    print("Invalid input")
            else:
                print("No Bluetooth devices found")
                
        elif choice == "3":
            print(f"Waiting to receive files...")
            print("Press Ctrl+C to return to menu")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                continue
                
        elif choice == "4":
            print("Shutting down...")
            break
            
        else:
            print("Invalid choice. Please try again.")

    # Clean up
    bluetooth_task.cancel()
    try:
        await bluetooth_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main()) 