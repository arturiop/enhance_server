import subprocess
import os
import shutil
import glob

class EnhanceServices:

    def enhance_video(self, filepath: str, loop_cnt: str = '0'):
        """loop_cnt - help create folder to enhance to not mix with already created"""

        FRAMES_DIR = f"temp_frames{loop_cnt}"
        ENHANCED_FRAMES_DIR = f"enhanced_frames{loop_cnt}"
        MODEL_NAME = "RealESRGAN_x4plus_anime_6B" # RealESRGAN_x2plus #"RealESRGAN_x4plus_anime_6B"

        os.makedirs(FRAMES_DIR, exist_ok=True)
        os.makedirs(ENHANCED_FRAMES_DIR, exist_ok=True)

        filename = os.path.basename(filepath)

        output_path = os.path.join("processed_videos", f"enh_{filename}")

        # Step 1: Extract frames
        if os.path.exists(ENHANCED_FRAMES_DIR) and len(os.listdir(ENHANCED_FRAMES_DIR)) and len(os.listdir(FRAMES_DIR)):
            enhanced_files = set(os.listdir(ENHANCED_FRAMES_DIR))
            for f in enhanced_files:
                name = f[:-8] + '.png'
                original_path = os.path.join(FRAMES_DIR, name)
                if os.path.exists(original_path):
                    os.remove(original_path)
        else: 
            subprocess.run([
                "ffmpeg", "-i", filepath, os.path.join(FRAMES_DIR, "frame_%04d.png")
            ], check=True)

        # Step 2: Run Real-ESRGAN on frames
        subprocess.run([
            "python", "inference_realesrgan.py",
            "-n", MODEL_NAME,
            "-i", os.path.abspath(FRAMES_DIR),
            "-o", os.path.abspath(ENHANCED_FRAMES_DIR),
            "--fp32",
            "--tile", "128",
        ], cwd="Real-ESRGAN", check=True)

        print("✅ Frames enhanced successfully!")

        # Step 3: Reassemble video
        input_pattern = os.path.join(ENHANCED_FRAMES_DIR, "frame_%04d_out.png")

        # Check if the frames exist
        if not glob.glob(input_pattern.replace("%04d", "*")):
            raise RuntimeError("❌ No enhanced frames found!")
        
        # if not os.path.exists(output_path):
        #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #     print('done makedir')

        subprocess.run([
            "ffmpeg", "-framerate", "24",
            "-i", input_pattern,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path,
            "-r", "24"
        ], check=True)

        # ❌ CLEANUP BE CAREFUL ❌
        shutil.rmtree(FRAMES_DIR)
        shutil.rmtree(ENHANCED_FRAMES_DIR)
        os.remove(filepath)

        return output_path
