
"""
REAL-TIME SERIAL IMU - Buffer Management for Immediate Response
Clears old serial data to ensure immediate response to IMU movement
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import time

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Install: pip install pyserial")

class RealTimeIMU:
    def __init__(self):
        # Current rotations - IMMEDIATE response
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

        # Control modes
        self.demo_mode = False
        self.demo_time = 0

        # Serial setup
        self.serial_port = None
        self.serial_connected = False

        # Buffer management - KEY TO REAL-TIME RESPONSE
        self.buffer_clear_interval = 0.05  # Clear buffer every 50ms
        self.last_buffer_clear = 0
        self.max_buffer_size = 100  # Maximum bytes to keep in buffer

        # Performance tracking
        self.data_count = 0
        self.last_data_time = 0

        # Setup matplotlib
        self.fig, self.ax = plt.subplots(subplot_kw=dict(projection='3d'), figsize=(12, 8))
        self.fig.suptitle('REAL-TIME IMU - Buffer Managed for Immediate Response', fontsize=16)

        # Connect keyboard
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # Initialize serial
        self.init_serial()

        print("⚡ REAL-TIME SERIAL IMU")
        print("=" * 35)
        print("🎯 SOLUTION: Proper buffer management")
        print("✅ Clears old data automatically") 
        print("✅ Only processes latest IMU data")
        print("✅ Immediate response to movement")
        print("")
        print("🎮 CONTROLS:")
        print("D - Toggle demo mode")
        print("R - Reset orientation") 
        print("B - Manual buffer clear")
        print("ESC - Quit")
        print("")

    def init_serial(self):
        """Initialize serial with proper buffer settings"""
        if not SERIAL_AVAILABLE:
            print("❌ pyserial not available")
            self.demo_mode = True
            return

        try:
            port_name = 'COM6'  # CHANGE THIS TO YOUR PORT
            print(f"🔌 Connecting to {port_name}...")

            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=115200,  # Match Arduino baud rate
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.01,  # Very short timeout for real-time
                write_timeout=0.01
            )

            # Wait for Arduino reset
            time.sleep(2)

            # CRITICAL: Clear any initial buffer data
            self.clear_serial_buffer()

            self.serial_connected = True
            print(f"✅ Connected to {port_name}")
            print("⚡ Real-time buffer management enabled")

        except Exception as e:
            print(f"❌ Serial connection failed: {e}")
            self.serial_connected = False
            self.demo_mode = True

    def clear_serial_buffer(self):
        """CRITICAL: Clear old data from serial buffer"""
        if not self.serial_port:
            return

        try:
            # Method 1: Flush input buffer
            self.serial_port.reset_input_buffer()

            # Method 2: Read and discard any remaining data
            old_timeout = self.serial_port.timeout
            self.serial_port.timeout = 0.001  # Very short timeout

            discarded_count = 0
            while self.serial_port.in_waiting > 0:
                self.serial_port.readline()
                discarded_count += 1
                if discarded_count > 50:  # Safety limit
                    break

            self.serial_port.timeout = old_timeout

            if discarded_count > 0:
                print(f"🗑️  Discarded {discarded_count} old data packets")

        except Exception as e:
            print(f"Buffer clear error: {e}")

    def read_latest_serial_data(self):
        """Read ONLY the most recent serial data - KEY FUNCTION"""
        if not self.serial_connected or not self.serial_port:
            return False

        try:
            current_time = time.time()

            # STEP 1: Clear buffer periodically to prevent lag buildup
            if current_time - self.last_buffer_clear > self.buffer_clear_interval:
                # If buffer is getting too full, clear old data
                if self.serial_port.in_waiting > self.max_buffer_size:
                    print(f"📦 Buffer size: {self.serial_port.in_waiting} - clearing old data")
                    self.clear_serial_buffer()

                self.last_buffer_clear = current_time

            # STEP 2: Read only the most recent complete data packet
            latest_data = None
            packets_discarded = 0

            while self.serial_port.in_waiting > 0:
                try:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        # Keep only the latest data, discard older packets
                        if latest_data is not None:
                            packets_discarded += 1
                        latest_data = line
                except:
                    break

            # STEP 3: Process the latest data only
            if latest_data:
                if packets_discarded > 0:
                    print(f"⏭️  Skipped {packets_discarded} old packets - using latest")

                values = latest_data.split(',')
                if len(values) >= 3:
                    try:
                        # IMMEDIATE assignment - no smoothing for real-time response
                        self.rotY = float(values[0])
                        self.rotX = float(values[1])
                        self.rotZ = float(values[2])

                        self.data_count += 1
                        self.last_data_time = current_time

                        # Debug output occasionally
                        if self.data_count % 50 == 0:
                            print(f"📊 Real-time data #{self.data_count}: X={self.rotX:.1f}° Y={self.rotY:.1f}° Z={self.rotZ:.1f}°")

                        return True

                    except ValueError:
                        print(f"Parse error: {latest_data}")

            return False

        except Exception as e:
            print(f"Serial read error: {e}")
            return False

    def update_demo(self):
        """Demo mode"""
        self.demo_time += 0.02
        self.rotX = 45 * np.sin(self.demo_time)
        self.rotY = 30 * np.cos(self.demo_time * 0.7)
        self.rotZ = 60 * np.sin(self.demo_time * 0.3)

    def draw_realtime_cube(self, size=2.0):
        """Draw cube with real-time indicators"""
        # Clear
        self.ax.clear()
        self.ax.set_xlim([-3, 3])
        self.ax.set_ylim([-3, 3])
        self.ax.set_zlim([-3, 3])

        # Cube vertices
        s = size / 2
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s],  [s, -s, s],  [s, s, s],  [-s, s, s]
        ])

        # Apply rotations
        rx = np.radians(-self.rotX)
        ry = np.radians(self.rotY)
        rz = np.radians(self.rotZ) #changed

        Rx = np.array([[1,0,0], [0,np.cos(rx),-np.sin(rx)], [0,np.sin(rx),np.cos(rx)]])
        Ry = np.array([[np.cos(ry),0,np.sin(ry)], [0,1,0], [-np.sin(ry),0,np.cos(ry)]])
        Rz = np.array([[np.cos(rz),-np.sin(rz),0], [np.sin(rz),np.cos(rz),0], [0,0,1]])

        R = Rz @ Ry @ Rx
        rotated_vertices = (R @ vertices.T).T

        # Draw cube faces with colors
        faces = [
            ([0, 1, 2, 3], '#FF6B6B'),  # Bottom - Red
            ([4, 7, 6, 5], '#4ECDC4'),  # Top - Teal
            ([0, 4, 5, 1], '#45B7D1'),  # Front - Blue
            ([2, 6, 7, 3], '#96CEB4'),  # Back - Green
            ([0, 3, 7, 4], '#FFEAA7'),  # Left - Yellow
            ([1, 5, 6, 2], '#DDA0DD')   # Right - Purple
        ]

        try:
            face_polygons = []
            face_colors = []

            for face_indices, color in faces:
                face_verts = rotated_vertices[face_indices]
                face_polygons.append(face_verts)
                face_colors.append(color)

            cube = Poly3DCollection(face_polygons, 
                                   facecolors=face_colors,
                                   edgecolors='black',
                                   alpha=0.8,
                                   linewidths=1.5)
            self.ax.add_collection3d(cube)

        except:
            # Fallback wireframe
            edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
            for edge in edges:
                points = rotated_vertices[edge]
                self.ax.plot3D(*points.T, 'b-', linewidth=2)

        # Coordinate axes
        self.ax.plot([0, 2.5], [0, 0], [0, 0], 'r-', linewidth=4, alpha=0.8)
        self.ax.plot([0, 0], [0, 2.5], [0, 0], 'g-', linewidth=4, alpha=0.8)
        self.ax.plot([0, 0], [0, 0], [0, 2.5], 'b-', linewidth=4, alpha=0.8)

        # Labels
        self.ax.set_xlabel('X (Roll)', fontweight='bold')
        self.ax.set_ylabel('Y (Pitch)', fontweight='bold')
        self.ax.set_zlabel('Z (Yaw)', fontweight='bold')

        # Title with real-time indicator
        if self.serial_connected and not self.demo_mode:
            data_age = time.time() - self.last_data_time if self.last_data_time > 0 else 0
            freshness = "🟢 LIVE" if data_age < 0.5 else "🟡 STALE" if data_age < 2 else "🔴 OLD"
            title = f'⚡ REAL-TIME: Roll={self.rotX:.1f}° Pitch={self.rotY:.1f}° Yaw={self.rotZ:.1f}° | {freshness}'
        else:
            title = f'🎮 DEMO: Roll={self.rotX:.1f}° Pitch={self.rotY:.1f}° Yaw={self.rotZ:.1f}°'

        self.ax.set_title(title, fontsize=12, fontweight='bold')

        # Status info
        buffer_size = self.serial_port.in_waiting if self.serial_port else 0
        status = f'Buffer: {buffer_size} bytes | Data rate: {self.data_count} packets'
        self.ax.text2D(0.02, 0.02, status, transform=self.ax.transAxes, fontsize=10)

    def draw_ui_panels(self):
        """Draw UI panels in figure coordinates to avoid overlaps"""

        # Clear any existing text
        for txt in self.fig.texts:
            txt.remove()

        # Values panel - Left side
        values_text = f'ROTATION VALUES\n\nRoll:  {self.rotX:6.1f}°\nPitch: {self.rotY:6.1f}°\nYaw:   {self.rotZ:6.1f}°'
        self.fig.text(0.02, 0.7, values_text, fontsize=12, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
                     verticalalignment='top')

        # Status panel - Left side, lower
        if self.serial_connected and not self.demo_mode:
            status_text = '📡 SERIAL CONNECTED\n⚡ Real-time IMU data'
            status_color = 'lightgreen'
        elif self.demo_mode:
            status_text = '🎮 DEMO MODE\n🔄 Simulated rotation'
            status_color = 'lightyellow'
        else:
            status_text = '❌ NO CONNECTION\n🔌 Check serial port'
            status_color = 'lightcoral'

        self.fig.text(0.02, 0.4, status_text, fontsize=10,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor=status_color, alpha=0.8),
                     verticalalignment='top')

        # Controls panel - Right side
        controls_text = 'CONTROLS\n\nD - Demo mode\nR - Reset rotation\nESC - Exit program'
        self.fig.text(0.88, 0.7, controls_text, fontsize=10,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
                     verticalalignment='top', horizontalalignment='left')

        # Performance panel - Right side, lower
        buffer_size = self.serial_port.in_waiting if self.serial_port else 0
        perf_text = f'PERFORMANCE\n\nBuffer: {buffer_size} bytes\nFPS: ~30'
        self.fig.text(0.88, 0.4, perf_text, fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                     verticalalignment='top', horizontalalignment='left')
    def update_plot(self, frame):
        """Update plot - real-time focused"""
        # Update rotations
        if self.serial_connected and not self.demo_mode:
            # Try to read latest serial data
            if not self.read_latest_serial_data():
                # No new data - keep current values (don't fallback to demo)
                pass
        else:
            # Demo mode
            self.update_demo()

        # Draw cube
        self.draw_realtime_cube()
        self.draw_ui_panels()

    def on_key_press(self, event):
        """Handle keyboard input"""
        if not event.key:
            return

        key = event.key.lower()

        if key == 'r':
            # Reset
            self.rotX = self.rotY = self.rotZ = 0
            print("🔄 Reset orientation")

        elif key == 'd':
            # Toggle demo
            self.demo_mode = not self.demo_mode
            print(f"🎮 Demo mode: {'ON' if self.demo_mode else 'OFF'}")

        elif key == 'b':
            # Manual buffer clear
            if self.serial_port:
                self.clear_serial_buffer()
                print("🗑️  Manual buffer clear")

        elif key == 'escape':
            plt.close('all')

    def start(self):
        """Start real-time visualization"""
        print("⚡ Starting REAL-TIME IMU visualization...")
        print("🎯 Move your IMU - should respond IMMEDIATELY!")
        print("📊 Watch console for buffer management info")
        print("")

        # Fast animation for real-time response
        ani = animation.FuncAnimation(self.fig, self.update_plot, 
                                    interval=25,  # 40 FPS for responsiveness
                                    blit=False,
                                    cache_frame_data=False)

        plt.tight_layout()
        plt.show()

        # Cleanup
        if self.serial_port:
            self.serial_port.close()

        return ani

if __name__ == "__main__":
    print("⚡ REAL-TIME SERIAL IMU - Buffer Management Solution")
    print("=" * 60)
    print("🎯 SOLUTION FOR BUFFER LAG:")
    print("✅ Clears old serial data automatically")
    print("✅ Processes only the latest IMU data")
    print("✅ Immediate response to movement")
    print("✅ No 2+ second delay")
    print("")
    print("IMPORTANT: Change COM6 to your Arduino port!")
    print("")

    # Create and start
    imu = RealTimeIMU()
    animation_obj = imu.start()
