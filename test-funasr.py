from funasr import AutoModel

model_dir = "FunAudioLLM/Fun-ASR-Nano-2512"

import time

wav_path = 'vad_example.wav'
model = AutoModel(
    model=model_dir,
    # vad_model="fsmn-vad",
    vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",    
)
start = time.perf_counter()
res = model.generate(input=[wav_path], cache={}, batch_size_s=0)
elapsed_s = time.perf_counter() - start
print(f"inference_time_s={elapsed_s:.4f}")
text = res[0]["text"]
print(text)
