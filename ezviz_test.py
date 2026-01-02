import sys
import io
from pyezviz.client import EzvizClient
import json
from datetime import datetime

# Fix encoding untuk Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class EzvizController:
    def __init__(self, username, password, region='apiieu.ezvizlife.com'):
        """
        Inisialisasi koneksi ke EZVIZ
        
        Args:
            username: Email/username akun EZVIZ
            password: Password akun EZVIZ
            region: Region URL server
                - apiieu.ezvizlife.com (Europe - default)
                - apiius.ezvizlife.com (United States)
                - apius.ezvizlife.com (United States alt)
                - apiieu.ezvizlife.com (Asia - gunakan EU endpoint)
        """
        self.username = username
        self.password = password
        self.region = region
        self.client = None
        
    def login(self):
        """Login ke akun EZVIZ"""
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Mencoba login ke EZVIZ...")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Region: {self.region}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Username: {self.username}")
            
            self.client = EzvizClient(self.username, self.password, self.region)
            self.client.login()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Login berhasil!")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Login gagal: {str(e)}")
            print(f"\n💡 Tips:")
            print("   - Pastikan username dan password benar")
            print("   - Coba region lain jika login gagal:")
            print("     • apiieu.ezvizlife.com (Europe/Asia)")
            print("     • apiius.ezvizlife.com (US)")
            return False
    
    def get_cameras(self):
        """Mendapatkan daftar semua kamera"""
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Mengambil daftar kamera...")
            # Gunakan get_device_infos untuk mendapatkan semua kamera
            devices = self.client.get_device_infos()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Ditemukan {len(devices)} kamera\n")
            
            for serial, device in devices.items():
                status_obj = device if hasattr(device, 'get') else {}
                print(f"{'='*60}")
                print(f"Nama: {status_obj.get('name', 'N/A')}")
                print(f"Serial: {serial}")
                print(f"Status: {'Online' if status_obj.get('status') == 1 else 'Offline'}")
                print(f"Model: {status_obj.get('device_sub_category', 'N/A')}")
                print(f"Versi: {status_obj.get('version', 'N/A')}")
                print(f"Alarm Notify: {'Aktif' if status_obj.get('alarm_notify') else 'Nonaktif'}")
                print(f"Privacy Mode: {'ON' if status_obj.get('switches', {}).get(2) else 'OFF'}")
                print(f"Audio: {'ON' if status_obj.get('switches', {}).get(0) else 'OFF'}")
                print(f"IR LED: {'ON' if status_obj.get('switches', {}).get(3) else 'OFF'}")
                print(f"{'='*60}\n")
            
            return devices
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal mengambil kamera: {str(e)}")
            return None
    
    def get_camera_status(self, serial):
        """Mendapatkan status detail kamera"""
        try:
            from pyezviz.camera import EzvizCamera
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengambil status kamera {serial}...")
            camera = EzvizCamera(self.client, serial)
            status = camera.status()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Status kamera:")
            print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
            return status
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e)}")
            return None
    
    def set_alarm(self, serial, enable=True):
        """Mengaktifkan/menonaktifkan alarm notification"""
        try:
            from pyezviz.camera import EzvizCamera
            import traceback
            
            action = "mengaktifkan" if enable else "menonaktifkan"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {action.capitalize()} alarm notify untuk {serial}...")
            
            camera = EzvizCamera(self.client, serial)
            # Konversi boolean ke integer (1 atau 0)
            result = camera.alarm_notify(1 if enable else 0)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Alarm notify berhasil {action} (result: {result})")
            return True
        except Exception as e:
            import traceback
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e) if str(e) else type(e).__name__}")
            print(f"    Detail: {traceback.format_exc()}")
            return False
    
    def move_camera(self, serial, direction, speed=5):
        """
        Menggerakkan kamera (PTZ)
        
        Args:
            serial: Serial number kamera
            direction: 'up', 'down', 'left', 'right'
            speed: Kecepatan gerakan (1-9)
        """
        try:
            from pyezviz.camera import EzvizCamera
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Menggerakkan kamera ke {direction}...")
            camera = EzvizCamera(self.client, serial)
            camera.move(direction, speed)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Kamera bergerak ke {direction}")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e)}")
            return False
    
    def set_privacy_mode(self, serial, enable=True):
        """Mengaktifkan/menonaktifkan privacy mode"""
        try:
            from pyezviz.camera import EzvizCamera
            
            action = "mengaktifkan" if enable else "menonaktifkan"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {action.capitalize()} privacy mode...")
            
            camera = EzvizCamera(self.client, serial)
            camera.switch_privacy_mode(enable)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Privacy mode berhasil {action}")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e)}")
            return False
    
    def reboot_camera(self, serial):
        """Restart kamera"""
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Merestart kamera {serial}...")
            # Device operations dilakukan melalui client
            self.client.device_operation(serial, "reboot")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Kamera direstart")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e)}")
            return False
    
    def set_audio(self, serial, enable=True):
        """Mengaktifkan/menonaktifkan audio kamera"""
        try:
            from pyezviz.camera import EzvizCamera
            
            action = "mengaktifkan" if enable else "menonaktifkan"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {action.capitalize()} audio kamera...")
            
            camera = EzvizCamera(self.client, serial)
            # Gunakan method wrapper langsung
            result = camera.switch_device_audio(1 if enable else 0)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Audio berhasil {action} (result: {result})")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e) if str(e) else type(e).__name__}")
            return False
    
    def set_ir_led(self, serial, enable=True):
        """Mengaktifkan/menonaktifkan IR LED (night vision)"""
        try:
            from pyezviz.camera import EzvizCamera
            
            action = "mengaktifkan" if enable else "menonaktifkan"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {action.capitalize()} IR LED...")
            
            camera = EzvizCamera(self.client, serial)
            # Gunakan method wrapper langsung
            result = camera.switch_device_ir_led(1 if enable else 0)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ IR LED berhasil {action} (result: {result})")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e) if str(e) else type(e).__name__}")
            return False
        except Exception as e:
            import traceback
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Gagal: {str(e) if str(e) else type(e).__name__}")
            print(f"    Detail: {traceback.format_exc()}")
            return False


def load_config_from_file(config_file='ezviz_config.json'):
    """Load konfigurasi dari file JSON"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return (
                config['ezviz']['username'],
                config['ezviz']['password'],
                config['ezviz'].get('region', 'eu')
            )
    except FileNotFoundError:
        return None, None, None
    except Exception as e:
        print(f"Error membaca config: {e}")
        return None, None, None


def get_credentials_interactive():
    """Minta kredensial secara interaktif"""
    print("\n" + "="*60)
    print("           MASUKKAN KREDENSIAL EZVIZ")
    print("="*60)
    username = input("\nEmail EZVIZ: ").strip()
    password = input("Password: ").strip()
    
    print("\nPilih Region:")
    print("1. Europe/Asia (apiieu.ezvizlife.com) - Recommended")
    print("2. United States (apiius.ezvizlife.com)")
    print("3. US Alternative (apius.ezvizlife.com)")
    region_choice = input("\nPilihan (1-3) [default: 1]: ").strip() or "1"
    
    region_map = {
        "1": "apiieu.ezvizlife.com",
        "2": "apiius.ezvizlife.com", 
        "3": "apius.ezvizlife.com"
    }
    region = region_map.get(region_choice, "apiieu.ezvizlife.com")
    
    return username, password, region


def main():
    """Contoh penggunaan script"""
    
    print("="*60)
    print("         EZVIZ Camera Controller - Test Script")
    print("="*60)
    
    # Coba load dari config file dulu
    username, password, region = load_config_from_file()
    
    # Jika tidak ada config file atau kredensial masih default, minta input
    if not username or username == "your-email@example.com":
        print("\n⚠ Config file tidak ditemukan atau belum diisi.")
        print("\nAnda bisa:")
        print("1. Input kredensial sekarang (sementara)")
        print("2. Buat file 'ezviz_config.json' dari 'ezviz_config.example.json'")
        
        choice = input("\nPilihan (1/2): ").strip()
        
        if choice == "1":
            username, password, region = get_credentials_interactive()
        else:
            print("\n📝 Cara membuat config file:")
            print("1. Copy 'ezviz_config.example.json' menjadi 'ezviz_config.json'")
            print("2. Edit file tersebut dan isi username, password, dan region")
            print("3. Jalankan script ini lagi")
            return
    else:
        print(f"\n✓ Menggunakan kredensial dari config file")
        print(f"  Region: {region}")
    
    # Inisialisasi controller
    controller = EzvizController(username, password, region)
    
    # Login
    if not controller.login():
        print("\n⚠ Login gagal. Periksa username/password dan koneksi internet.")
        return
    
    # Dapatkan daftar kamera
    cameras = controller.get_cameras()
    
    if not cameras:
        print("\n⚠ Tidak ada kamera ditemukan atau gagal mengambil data.")
        return
    
    # Ambil serial kamera pertama untuk testing
    first_serial = list(cameras.keys())[0]
    print(f"\n📹 Menggunakan kamera pertama untuk testing: {first_serial}")
    
    # Test berbagai fungsi
    print("\n" + "="*60)
    print("TESTING FUNGSI-FUNGSI KAMERA")
    print("="*60)
    
    # 1. Get status detail
    print("\n1. Status Detail Kamera:")
    controller.get_camera_status(first_serial)
    
    # 2. Test alarm notification
    print("\n2. Testing Alarm Notification:")
    controller.set_alarm(first_serial, enable=True)
    
    # 3. Test switches (Audio, IR LED, dll)
    print("\n3. Testing Device Switches:")
    controller.set_audio(first_serial, enable=True)
    controller.set_ir_led(first_serial, enable=True)
    
    # 3. Test PTZ (jika kamera support)
    # Uncomment untuk test gerakan kamera
    # print("\n3. Testing PTZ Movement:")
    # controller.move_camera(first_serial, 'right', speed=5)
    
    # 4. Test privacy mode
    # Uncomment untuk test privacy mode
    # print("\n4. Testing Privacy Mode:")
    # controller.set_privacy_mode(first_serial, enable=False)
    
    print("\n" + "="*60)
    print("✓ Testing selesai!")
    print("="*60)


if __name__ == "__main__":
    main()
