from fawkes.protection import Fawkes
import gradio as gr

def predict(level, img):
  fwks = Fawkes("extractor_2", '0', 1, mode=level)
  fwks.run_protection([img], format='jpeg')
  splt = img.split(".")
  return splt[0] + "_cloaked." + splt[1]

gr.Interface(fn=predict, inputs=[gr.inputs.Dropdown(["low", "mid", "high"], label="Protection Level"), gr.inputs.Image(type='filepath')], outputs=gr.outputs.Image(type="pil")).launch(share=True)