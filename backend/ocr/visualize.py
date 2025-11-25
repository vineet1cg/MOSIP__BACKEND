from PIL import Image, ImageDraw, ImageFont

def draw_boxes(pil_image, boxes):
    im = pil_image.convert("RGBA")
    draw = ImageDraw.Draw(im)
    for b in boxes:
        left, top, w, h = b["left"], b["top"], b["width"], b["height"]
        draw.rectangle([left, top, left+w, top+h], outline="red", width=2)
        draw.text((left, top-10), f'{b.get("text","")} ({b.get("conf",0):.2f})', fill="red")
    return im
