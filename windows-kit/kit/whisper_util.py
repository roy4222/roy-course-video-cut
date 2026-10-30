"""faster-whisper loader. Device from KIT_WHISPER_DEVICE (cpu | cuda | auto; default cpu).
On Windows with an NVIDIA GPU, `setup.ps1 -Cuda` installs the cuBLAS/cuDNN wheels; their DLL folders are added here."""
import glob, os, sys

_cache = {}


def _add_cuda_dlls():
    if sys.platform != 'win32':
        return
    for sp in sys.path:
        for d in glob.glob(os.path.join(sp, 'nvidia', '*', 'bin')):
            try:
                os.add_dll_directory(d)
            except OSError:
                pass
            os.environ['PATH'] = d + os.pathsep + os.environ.get('PATH', '')


def model(name='small', threads=None):
    from faster_whisper import WhisperModel
    dev = os.environ.get('KIT_WHISPER_DEVICE', 'cpu').lower()
    key = (name, dev)
    if key in _cache:
        return _cache[key]
    m = None
    if dev in ('cuda', 'auto'):
        _add_cuda_dlls()
        try:
            m = WhisperModel(name, device='cuda', compute_type='float16')
            # a tiny transcription forces the CUDA libraries to load now, not in the middle of a job
            import numpy as np
            list(m.transcribe(np.zeros(16000, dtype='float32'), language='zh')[0])
            print(f'[whisper] {name} on CUDA', flush=True)
        except Exception as e:
            print(f'[whisper] CUDA not usable ({str(e)[:120]}); falling back to CPU', flush=True)
            m = None
    if m is None:
        th = threads or int(os.environ.get('KIT_WHISPER_THREADS', '0')) or max(2, min(8, (os.cpu_count() or 4) // 3))
        m = WhisperModel(name, device='cpu', compute_type=os.environ.get('KIT_WHISPER_COMPUTE', 'float32'), cpu_threads=th)  # int8 gave empty/garbled zh output on some CPUs
    _cache[key] = m
    return m
