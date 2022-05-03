import numpy as np

# from PIL import Image

def hist(image, output):
    image = image.astype(np.float32)

    gray = np.empty(image.shape[:2], dtype=np.float32)
    gray[:,:] = 0.299 * image[:,:,0] + 0.587 * image[:,:,1] + 0.114 * image[:,:,2]

    Cr = (image[:,:,0] - gray) * 0.713 + 128
    Cb = (image[:,:,2] - gray) * 0.564 + 128

    binned_gray = np.clip(gray, 0, 255).astype(np.uint8)

    # [0, ..., 256] where 256 is the rightmost edge
    hist, bins = np.histogram(binned_gray, bins=np.arange(257), density=True)
    cdf = np.cumsum(hist)

    eq = cdf[binned_gray]
    eq = eq * 255.0
    eq = np.clip(eq, 0, 255)

    output[:,:,0] = np.clip(eq + (Cr - 128) * 1.4, 0, 255).astype(np.uint8)
    output[:,:,1] = np.clip(eq - 0.343 * (Cb - 128) - 0.711 * (Cr - 128), 0, 255).astype(np.uint8)
    output[:,:,2] = np.clip(eq + 1.765 * (Cb - 128), 0, 255).astype(np.uint8)

    # img = Image.fromarray(output)
    # img.save("hist_output.png")

    return output