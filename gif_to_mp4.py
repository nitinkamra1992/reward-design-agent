import os

import numpy as np
from moviepy.editor import ImageSequenceClip
from moviepy.video.io.ffmpeg_writer import ffmpeg_write_video
from PIL import Image, ImageSequence


def gif_to_mp4_with_identical_duration(src_path, dst_path, default_fps=24):
    """Convert GIF to MP4, preserving identical total duration."""
    with Image.open(src_path) as gif:
        frames = []
        durations = []
        base_size = gif.size  # (width, height)

        for frame in ImageSequence.Iterator(gif):
            img = frame.convert("RGB")
            if img.size != base_size:
                img = img.resize(base_size)
            frames.append(np.array(img))

            # Get per-frame duration safely
            dur = frame.info.get("duration")
            if dur is None or not isinstance(dur, (int, float)) or dur <= 0:
                dur = 100  # default 100ms
            durations.append(dur)

        frame_count = len(frames)
        if frame_count == 0:
            raise ValueError("GIF has no frames!")

        total_duration = sum(durations) / 1000.0  # seconds
        if total_duration <= 0 or not np.isfinite(total_duration):
            total_duration = frame_count / default_fps

        fps = frame_count / total_duration if total_duration > 0 else default_fps
        if not np.isfinite(fps) or fps <= 0:
            fps = default_fps

        print(f"  → {frame_count} frames, {total_duration:.2f}s total, fps={fps:.2f}")

        # Ensure all frames are numpy arrays of identical shape
        height, width = frames[0].shape[0], frames[0].shape[1]
        for i, f in enumerate(frames):
            if f.shape[0] != height or f.shape[1] != width:
                raise ValueError(f"Frame {i} has inconsistent size {f.shape}")

        # Create ImageSequenceClip explicitly with correct fps
        clip = ImageSequenceClip(frames, fps=float(fps))

        # Force all metadata to be numeric
    # Force valid metadata
    fps = float(fps)
    clip.fps = fps
    clip.size = (width, height)
    clip.duration = float(total_duration)
    clip.end = float(total_duration)
    clip._fps = fps
    clip._duration = clip.duration
    clip._size = clip.size

    # --- PATCH: ensure reader has valid fps ---
    class DummyReader:
        def __init__(self, fps):
            self.fps = fps

    clip.reader = DummyReader(fps)

    print(
        "DEBUG: clip.fps =",
        clip.fps,
        "clip.duration =",
        clip.duration,
        "clip.size =",
        clip.size,
    )

    ffmpeg_write_video(
        clip=clip,
        filename=dst_path,
        fps=fps,
        codec="libx264",
        preset="medium",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )

    clip.close()


def convert_all_gifs(source_dir, target_dir):
    os.makedirs(target_dir, exist_ok=True)

    for filename in os.listdir(source_dir):
        if filename.lower().endswith(".gif"):
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(target_dir, os.path.splitext(filename)[0] + ".mp4")

            try:
                print(f"🎞️ Converting {filename} ...")
                gif_to_mp4_with_identical_duration(src_path, dst_path)
                print(f"✅ Saved {dst_path}")
            except Exception as e:
                print(f"⚠️ Skipping {filename}: {e}")

    print("🎉 All GIFs processed.")


if __name__ == "__main__":
    source_folder = "docs/videos/eureka"
    target_folder = "docs/videos/eureka"
    convert_all_gifs(source_folder, target_folder)
