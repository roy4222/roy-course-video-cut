"""OpenRouter TTS helpers (google/gemini-3.8-flash-tts, voice Enceladus).

API key: environment variable OPENROUTER_API_KEY (make_episode.py loads it from the kit's .env).
The key is only sent in the Authorization header; it is never printed or written to disk.

Quick test (one short request, costs a fraction of a cent):
    python -m kit.tts_openrouter --test "你好，這是測試。" test.wav
"""
import json, os, re, subprocess, sys, time, urllib.request, urllib.error

DEFAULT_MODEL = os.environ.get('KIT_TTS_MODEL', 'google/gemini-3.8-flash-tts')
DEFAULT_VOICE = os.environ.get('KIT_TTS_VOICE', 'Enceladus')
DEFAULT_INS = os.environ.get('KIT_TTS_INSTRUCTIONS') or (
    "Speak in Mandarin Chinese with a Taiwan Mandarin accent (台灣國語口音), like a warm, clear, friendly "
    "teacher explaining to a complete beginner, at a moderate, unhurried pace.")
API = 'https://openrouter.ai/api/v1'


def _key():
    k = os.environ.get('OPENROUTER_API_KEY', '').strip()
    if not k or k.startswith('sk-or-v1-xxxx') or k == 'your-key-here':
        raise SystemExit('OPENROUTER_API_KEY is not set. Copy .env.example to .env and put your OpenRouter key there.')
    return k


def synth(text, out_wav, model=DEFAULT_MODEL, voice=DEFAULT_VOICE, ins=DEFAULT_INS, tries=12):
    """Synthesize `text` to a 24 kHz mono WAV. Retries on 429/5xx with exponential back-off.
    Returns the OpenRouter generation id (used to look up the cost) or None."""
    key = _key()
    body = {'model': model, 'input': text, 'voice': voice, 'response_format': 'pcm'}
    if ins:
        body['instructions'] = ins
    wait = 5
    for k in range(tries):
        req = urllib.request.Request(API + '/audio/speech', data=json.dumps(body).encode('utf-8'),
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        try:
            r = urllib.request.urlopen(req, timeout=300)
            data = r.read()
            ct = r.headers.get('Content-Type', '')
            m = re.search(r'rate=(\d+)', ct)
            sr = m.group(1) if m else '24000'
            if len(data) < 2000:
                raise RuntimeError('short audio (%d bytes)' % len(data))
            with open(out_wav + '.pcm', 'wb') as f:
                f.write(data)
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 's16le', '-ar', sr, '-ac', '1', '-i',
                            out_wav + '.pcm', '-ar', '24000', out_wav], check=True)
            os.remove(out_wav + '.pcm')
            return r.headers.get('X-Generation-Id')
        except urllib.error.HTTPError as e:
            print(f'  TTS HTTP {e.code} (try {k + 1}/{tries}), waiting {wait}s', file=sys.stderr, flush=True)
            if e.code in (401, 402, 403):
                raise SystemExit(f'OpenRouter refused the request (HTTP {e.code}): check the key / credits in .env')
            if e.code not in (408, 425, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, RuntimeError, ConnectionError) as e:
            print('  TTS error', str(e)[:120], file=sys.stderr, flush=True)
        time.sleep(wait)
        wait = min(wait * 2, 90)
    raise RuntimeError('TTS gave up after %d tries' % tries)


def cost(gid):
    """US$ cost of one generation (None if OpenRouter has not published it yet)."""
    if not gid:
        return None
    key = _key()
    for _ in range(8):
        time.sleep(2)
        try:
            req = urllib.request.Request(API + '/generation?id=' + gid, headers={'Authorization': 'Bearer ' + key})
            return json.load(urllib.request.urlopen(req, timeout=30))['data'].get('total_cost')
        except Exception:
            pass
    return None


def trim(src, dst):
    """Trim leading/trailing silence (-45 dB) and normalise to 24 kHz mono."""
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
                    'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse',
                    '-ar', '24000', '-ac', '1', dst], check=True)


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--test':
        g = synth(sys.argv[2], sys.argv[3])
        print('wrote', sys.argv[3], 'cost US$', cost(g))
    else:
        print(__doc__)
