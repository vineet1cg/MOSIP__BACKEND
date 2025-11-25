import difflib

def ensemble_fuse(trocr_res, tess_res, settings):
    trocr_conf = trocr_res.get("score", 0.0)
    tess_conf = tess_res.get("score", 0.0)
    chosen = None
    final_text = ""
    if trocr_conf >= settings.TROCR_CONF_THRESHOLD:
        final_text = trocr_res.get("text", "")
        chosen = "trocr"
    elif tess_conf > trocr_conf:
        final_text = tess_res.get("text", "")
        chosen = "tesseract"
    else:
        # merge line-level with difflib
        t1 = trocr_res.get("text", "").splitlines()
        t2 = tess_res.get("text", "").splitlines()
        if not t1 and not t2:
            final_text = ""
        elif not t1:
            final_text = "\n".join(t2)
        elif not t2:
            final_text = "\n".join(t1)
        else:
            # use SequenceMatcher quick union
            matcher = difflib.SequenceMatcher(None, "\n".join(t1), "\n".join(t2))
            blocks = matcher.get_matching_blocks()
            # simple pick union: choose the longer text
            final_text = t1[0] if len("\n".join(t1)) >= len("\n".join(t2)) else t2[0]
            final_text = "\n".join([x for x in (t1 + t2)])
        chosen = "merged"
    return {"text": final_text, "chosen": chosen}
