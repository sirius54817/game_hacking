import socket
import json
import os
import asyncio
from bleak import BleakClient, BleakScanner
from typing import Dict, Optional
from models.file_manager import FileManager

class TransferManager:
    def __init__(self, file_manager: FileManager, host: str = '0.0.0.0', port: int = 5000):
        self.file_manager = file_manager
        self.host = host
        self.port = port
        self.chunk_size = 8192  # 8KB chunks for transfer
        self.characteristic_uuid = "0000FFE1-0000-1000-8000-00805F9B34FB"  # Standard BLE UUID

    def start_wifi_server(self):
        """Start a WiFi server to receive files"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client, addr = server.accept()
            print(f"Connection from {addr}")
            self._handle_incoming_connection(client)

    def send_file_wifi(self, file_metadata: Dict, target_host: str, target_port: int):
        """Send an encrypted file over WiFi"""
        try:
            # Connect to receiver
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_host, target_port))

            # Send metadata
            metadata_json = json.dumps(file_metadata)
            sock.send(len(metadata_json).to_bytes(4, 'big'))
            sock.send(metadata_json.encode())

            # Send encrypted file
            file_path = os.path.join(
                self.file_manager.storage_path, 
                file_metadata['encrypted_filename']
            )
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    sock.send(chunk)

            print("File sent successfully")
            sock.close()

        except Exception as e:
            print(f"Error sending file: {e}")

    def _handle_incoming_connection(self, client_socket):
        """Handle incoming file transfer connection"""
        try:
            # Receive metadata size
            metadata_size = int.from_bytes(client_socket.recv(4), 'big')
            
            # Receive metadata
            metadata_json = client_socket.recv(metadata_size).decode()
            metadata = json.loads(metadata_json)

            # Prepare file path
            save_path = os.path.join(
                self.file_manager.storage_path, 
                metadata['encrypted_filename']
            )

            # Receive and save file
            with open(save_path, 'wb') as f:
                while True:
                    chunk = client_socket.recv(self.chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

            print(f"File received successfully: {metadata['original_filename']}")

        except Exception as e:
            print(f"Error receiving file: {e}")
        finally:
            client_socket.close()

    async def start_bluetooth_server(self):
        """Start a Bluetooth server to receive files"""
        print("Starting Bluetooth server (advertising)...")
        
        # This is a simplified version - in production you'd want to implement
        # proper GATT server functionality
        while True:
            try:
                # Scan for clients trying to connect
                devices = await BleakScanner.discover()
                for device in devices:
                    if device.name and "SecureFileTransfer" in device.name:
                        print(f"Found client device: {device.name}")
                        async with BleakClient(device.address) as client:
                            await self._handle_bluetooth_connection(client)
            except Exception as e:
                print(f"Bluetooth server error: {e}")
            await asyncio.sleep(1)

    async def send_file_bluetooth(self, file_metadata: Dict, target_address: str):
        """Send an encrypted file over Bluetooth"""
        try:
            async with BleakClient(target_address) as client:
                # Send metadata
                metadata_json = json.dumps(file_metadata)
                size_bytes = len(metadata_json).to_bytes(4, 'big')
                await client.write_gatt_char(
                    self.characteristic_uuid,
                    size_bytes + metadata_json.encode()
                )

                # Send encrypted file
                file_path = os.path.join(
                    self.file_manager.storage_path, 
                    file_metadata['encrypted_filename']
                )
                
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        await client.write_gatt_char(
                            self.characteristic_uuid,
                            chunk
                        )

                print("File sent successfully over Bluetooth")

        except Exception as e:
            print(f"Error sending file over Bluetooth: {e}")

    async def _handle_bluetooth_connection(self, client):
        """Handle incoming Bluetooth file transfer"""
        try:
            # Set up notification handler
            received_data = bytearray()
            
            def notification_handler(sender, data):
                nonlocal received_data
                received_data.extend(data)

            # Start listening for data
            await client.start_notify(
                self.characteristic_uuid,
                notification_handler
            )

            # Wait for complete file
            while True:
                if len(received_data) >= 4:
                    metadata_size = int.from_bytes(received_data[:4], 'big')
                    if len(received_data) >= metadata_size + 4:
                        metadata_json = received_data[4:metadata_size+4].decode()
                        metadata = json.loads(metadata_json)
                        file_data = received_data[metadata_size+4:]
                        break
                await asyncio.sleep(0.1)

            # Save received file
            save_path = os.path.join(
                self.file_manager.storage_path, 
                metadata['encrypted_filename']
            )
            
            with open(save_path, 'wb') as f:
                f.write(file_data)

            print(f"File received successfully over Bluetooth: {metadata['original_filename']}")

        except Exception as e:
            print(f"Error receiving file over Bluetooth: {e}")
        finally:
            await client.stop_notify(self.characteristic_uuid)

    async def discover_bluetooth_devices(self):
        """Discover nearby Bluetooth devices"""
        print("Scanning for Bluetooth devices...")
        devices = await BleakScanner.discover()
        return [(d.address, d.name or "Unknown", d.metadata) for d in devices]

    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1" 