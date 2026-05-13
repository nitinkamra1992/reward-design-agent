import os

from PIL import Image, ImageSequence

if __name__ == "__main__":
    # Directory containing GIFs
    input_dir = "eureka_temp"

    for filename in os.listdir(input_dir):
        print(filename)
        if filename.lower().endswith(".gif"):
            filepath = os.path.join(input_dir, filename)
            gif = Image.open(filepath)

            frames_1, frames_2 = [], []
            durations = []

            for frame in ImageSequence.Iterator(gif):
                w, h = frame.size
                left_half = frame.crop((0, 0, w // 2, h))
                right_half = frame.crop((w // 2, 0, w, h))

                frames_1.append(left_half.copy())
                frames_2.append(right_half.copy())

                # Save each frame's duration
                durations.append(min(frame.info["duration"], 100))

            base_name = os.path.splitext(filename)[0]
            output_1 = os.path.join(input_dir, f"{base_name}-1.gif")
            output_2 = os.path.join(input_dir, f"{base_name}-2.gif")

            frames_1[0].save(
                output_1,
                save_all=True,
                append_images=frames_1[1:],
                loop=0,
                duration=durations,
                transparency=gif.info.get("transparency"),
                disposal=2,
            )
            frames_2[0].save(
                output_2,
                save_all=True,
                append_images=frames_2[1:],
                loop=0,
                duration=durations,
                transparency=gif.info.get("transparency"),
                disposal=2,
            )

            print(f"✅ Split {filename} into {output_1} and {output_2}")
