#!/usr/bin/env python3
"""
Camera diagnostic tool for Raspberry Pi
Helps identify camera issues and optimal settings
"""

import cv2
import time
import logging

logging.basicConfig(level=logging.INFO)

def test_camera(camera_index):
    """Test a single camera with various settings"""
    print(f"\n=== Testing Camera {camera_index} ===")
    
    # Test with different backends
    backends = [
        ("Default", None),
        ("V4L2", cv2.CAP_V4L2),
        ("GSTREAMER", cv2.CAP_GSTREAMER)
    ]
    
    for backend_name, backend in backends:
        print(f"\nTrying {backend_name} backend...")
        
        try:
            if backend is None:
                camera = cv2.VideoCapture(camera_index)
            else:
                camera = cv2.VideoCapture(camera_index, backend)
            
            if not camera.isOpened():
                print(f"  ❌ Failed to open camera with {backend_name}")
                continue
            
            print(f"  ✅ Camera opened with {backend_name}")
            
            # Get default properties
            width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = camera.get(cv2.CAP_PROP_FPS)
            
            print(f"  Default: {int(width)}x{int(height)} @ {fps}fps")
            
            # Test reading frames
            success_count = 0
            for i in range(10):
                ret, frame = camera.read()
                if ret:
                    success_count += 1
                time.sleep(0.1)
            
            print(f"  Frame read success: {success_count}/10")
            
            if success_count > 5:  # If more than half successful
                # Test different resolutions
                resolutions = [(640, 480), (320, 240), (160, 120)]
                
                for w, h in resolutions:
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                    
                    actual_w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    ret, frame = camera.read()
                    if ret:
                        print(f"  ✅ {w}x{h} -> {actual_w}x{actual_h} (working)")
                    else:
                        print(f"  ❌ {w}x{h} -> {actual_w}x{actual_h} (failed)")
                
                # Test MJPEG codec
                camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                ret, frame = camera.read()
                if ret:
                    print(f"  ✅ MJPEG codec working")
                else:
                    print(f"  ❌ MJPEG codec failed")
            
            camera.release()
            
        except Exception as e:
            print(f"  ❌ Exception with {backend_name}: {e}")

def main():
    print("🔍 Raspberry Pi Camera Diagnostic Tool")
    print("=" * 50)
    
    # Check for cameras
    available_cameras = []
    for i in range(10):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            available_cameras.append(i)
            print(f"📷 Found camera at index {i}")
        camera.release()
    
    if not available_cameras:
        print("❌ No cameras found!")
        return
    
    print(f"\n📋 Found {len(available_cameras)} camera(s): {available_cameras}")
    
    # Test each camera
    for camera_index in available_cameras:
        test_camera(camera_index)
    
    print("\n" + "=" * 50)
    print("💡 Tips for common issues:")
    print("- If no cameras found: Check USB connections")
    print("- If camera opens but no frames: Try different USB port")
    print("- If high resolution fails: Your camera may not support it")
    print("- If MJPEG fails: Camera may only support raw formats")

if __name__ == "__main__":
    main()
