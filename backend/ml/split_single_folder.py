import os
import random
import shutil

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

def split_dataset(crop_path, split_ratio=0.8):
    for cls in os.listdir(crop_path):
        cls_path = os.path.join(crop_path, cls)

        if not os.path.isdir(cls_path):
            continue
        if cls.lower() in ["train", "val"]:
            continue

        images = [
            f for f in os.listdir(cls_path)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]

        random.shuffle(images)
        split = int(len(images) * split_ratio)

        for phase, imgs in {
            "train": images[:split],
            "val": images[split:]
        }.items():
            dst = os.path.join(crop_path, phase, cls)
            os.makedirs(dst, exist_ok=True)

            for img in imgs:
                shutil.copy(
                    os.path.join(cls_path, img),
                    os.path.join(dst, img)
                )

if __name__ == "__main__":
    split_dataset("dataset/rice")
    split_dataset("dataset/wheat")
