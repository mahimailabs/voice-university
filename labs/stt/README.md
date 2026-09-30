# STT from Scratch lab

A small offline CTC digit-sequence recognizer. All model weights start randomly.
This is not general speech recognition or a stateful streaming service.

## Run

Use Python 3.14 (the recorded environment) and a virtual environment. Install
`pip install -r requirements.txt`. Download the source recordings:

```sh
git clone https://github.com/Jakobovski/free-spoken-digit-dataset.git fsdd
git -C fsdd checkout 26eb9aaf76e81b692f806f9140c2d2777410d7a1
python lab.py --data fsdd --out my-run --epochs 60 --threads 4
python probes.py --data fsdd --run my-run
python overfit.py --data fsdd --out my-overfit.json
```

Results under `run/` are the recorded development experiment. `pilot-12/` retains
the earlier short run. Do not overwrite them when reproducing. The script default
is a short 12-epoch run; pass 60 explicitly for the published configuration.

## Scope and provenance

Training uses 600 generated sequences from george, jackson, lucas and nicolas.
Validation uses 120 sequences from theo. Evaluation uses 120 from yweweler.
Sequences contain 1–3 digits from the same speaker, sampled with replacement,
with 100 ms zero padding after every source clip. This is NOT FSDD's standard split.
The manifest records every source filename; generated examples are not independent
source recordings. Sampling seeds are 17/18/19, with train seed 17.

The twelve-epoch pilot was inspected before extending training to sixty epochs.
The evaluation speaker was therefore already seen during development. The results
are development evidence, not an untouched final test or production benchmark.
Epoch selection uses validation digit edit rate, retaining the earliest tie.

Training time includes validation each epoch but excludes data preparation.
Forward timing is 30 repetitions of one example after 3 warmups, without features,
decoding, I/O, networking or queueing. Four PyTorch CPU threads; see results.json
for platform/library versions. There is no promise of bit-identical cross-platform
training or identical runtime. Memory, concurrency and end-to-end latency were not
benchmarked.

The feature recipe is linear log-power STFT, not mel: 8 kHz, FFT 256, window 200,
hop 80, center=False, Hann window, per-utterance scalar standardisation. The
bidirectional GRU and normalisation make the model offline. Prefix probes recompute
the model from scratch; they do not implement incremental streaming.

## Audio attribution

Source: Free Spoken Digit Dataset, Jakobovski and contributors:
https://github.com/Jakobovski/free-spoken-digit-dataset
Revision: 26eb9aaf76e81b692f806f9140c2d2777410d7a1
Licence: Creative Commons Attribution-ShareAlike 4.0 International
https://creativecommons.org/licenses/by-sa/4.0/

The included example WAVs are adaptations: source recordings were concatenated
with added zero-valued silence. They remain CC BY-SA 4.0. Individual source files
for these examples are recorded in run/results.json and run/manifest.json.
No endorsement by the dataset contributors is implied. The small excerpts in the
course use the same attribution and licence. Retain this notice when redistributing.

## Extensions

The course discusses contextual biasing, pretrained adaptation and a causal
encoder as separate experiments. They are not implemented or measured by this lab.
`probes.py` includes a teaching beam decoder and synthetic Gaussian-noise probes.
It does not model a real phone network.
