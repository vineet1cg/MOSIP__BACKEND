from transformers import AutoProcessor, AutoModelForCausalLM
import torch
import math

class TroCRPipeline:
    def __init__(self, model_name="microsoft/trocr-base-handwritten", device="cpu"):
        self.device = torch.device(device)
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)

    def predict(self, pil_image):
        # processor expects PIL images
        inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)
        # generate with output_scores
        out = self.model.generate(**inputs, return_dict_in_generate=True, output_scores=True, max_length=1024)
        # decode tokens to string
        decoded = self.processor.batch_decode(out.sequences, skip_special_tokens=True)[0]
        # compute token-level confidence: average of softmax probs for chosen tokens
        scores = out.scores  # list of logits tensors per token step
        token_confidences = []
        import torch.nn.functional as F
        for step_scores in scores:
            probs = F.softmax(step_scores, dim=-1)
            # assume argmax token chosen; get its prob
            top_prob = probs.max().item()
            token_confidences.append(top_prob)
        if len(token_confidences) == 0:
            avg_conf = 0.0
        else:
            avg_conf = float(sum(token_confidences) / len(token_confidences))
        return {"text": decoded, "score": avg_conf, "token_confidences": token_confidences}
