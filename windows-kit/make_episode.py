#!/usr/bin/env python3
"""ml-video-kit: one command from an episode folder to a finished 1080p30 video.

    python make_episode.py <episode_dir> [steps...] [--workers N] [--nvenc] [--force] [--low-priority]

Steps (default = all, in this order; finished steps are skipped, so re-running resumes where it stopped):
    build     run <ep>/build.py  -> script.json, scenes.json, meta.json
    tts       OpenRouter Gemini TTS per scene + split back into lines -> voice/<line>.wav, voice/dur.json
    timeline  line timings + the HTML page -> film/index.html, film/timeline.js, cues.json
    layout    check text for overlap / out-of-frame / under-subtitle -> qc/layout.txt (warnings only)
    render    headless Chromium frames -> ffmpeg -> out/video.mp4 (silent picture, subtitles burned in)
    mix       place every voice line on the timeline + limiter -> out/mix_lim.wav
    mux       picture + audio, loudness -14 LUFS / true peak -1.2 dB -> epNN.mp4
    master    final peak limiter + AAC 192k + faststart (in place) -> epNN.mp4
    srt       subtitles file -> epNN.srt
    md        readable script with timestamps -> script.md
    qc        8 frames + Whisper listens to 3 lines to check A/V sync -> qc/
    yt        YouTube metadata (title, description, chapters, tags) -> youtube.json
Extra (not in "all"): stills  (end-of-scene preview images -> qc/pre/)

Naming steps explicitly always re-runs them. `--force` re-runs everything in the list.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time, wave, difflib

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
ALL = ['build', 'tts', 'timeline', 'layout', 'render', 'mix', 'mux', 'master', 'srt', 'md', 'qc', 'yt']
EXTRA = ['stills']
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace'); sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


# ---------------------------------------------------------------- small helpers
def rj(p, default=None):
    if default is not None and not os.path.exists(p):
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def wt(p, s):
    """Write text as UTF-8; leave the file (and its mtime) alone if the content is unchanged, so later steps are not redone."""
    if os.path.exists(p):
        try:
            with open(p, encoding='utf-8', newline='') as f:
                if f.read() == s: return
        except Exception:
            pass
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)
    os.replace(tmp, p)


def wj(p, obj, indent=0):
    wt(p, json.dumps(obj, ensure_ascii=False, indent=indent))


def rt(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def load_env():
    """Read KEY=VALUE lines from <kit>/.env without overriding real environment variables. Never prints values."""
    p = os.path.join(KIT, '.env')
    if not os.path.exists(p):
        return
    for line in rt(p).splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip(); v = v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v


def kit_dirs():
    """Keep the browser and the Whisper models inside the kit folder (e.g. on D:), as setup installed them."""
    b = os.path.join(KIT, '.browsers')
    if 'PLAYWRIGHT_BROWSERS_PATH' not in os.environ and os.path.isdir(b):
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = b
    os.environ.setdefault('HF_HOME', os.path.join(KIT, '.cache', 'huggingface'))
    os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')


def mem_gb():
    try:
        if sys.platform == 'win32':
            import ctypes
            class MS(ctypes.Structure):
                _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong)] + \
                           [(n, ctypes.c_ulonglong) for n in ('tot', 'avail', 'tpf', 'apf', 'tv', 'av', 'aev')]
            m = MS(); m.dwLength = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.tot / 2 ** 30
        if sys.platform == 'darwin':
            return int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True).stdout) / 2 ** 30
        for l in open('/proc/meminfo'):
            if l.startswith('MemTotal'):
                return int(l.split()[1]) / 2 ** 20
    except Exception:
        pass
    return 8


def auto_workers():
    """~4 CPU threads and ~6 GB RAM per render worker (one Chromium + one ffmpeg each), capped at 8.
    i7-13700F (24 threads) / 48 GB -> 6."""
    return max(1, min(8, (os.cpu_count() or 4) // 4, int(mem_gb() // 6)))


def low_priority():
    try:
        if sys.platform == 'win32':
            import ctypes  # BELOW_NORMAL_PRIORITY_CLASS; child processes (node, chrome, ffmpeg) inherit it
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
        else:
            os.nice(10)
    except Exception as e:
        print('could not lower priority:', e)


def need(tool):
    if not shutil.which(tool):
        sys.exit(f'"{tool}" was not found on PATH. Run setup (setup.ps1 / setup.sh) or see README 疑難排解.')


# ---------------------------------------------------------------- the episode
class Episode:
    def __init__(self, d, a):
        self.d = os.path.abspath(d); self.a = a
        if not os.path.isdir(self.d):
            sys.exit(f'episode folder not found: {self.d}')
        os.chdir(self.d)
        for sub in ('voice', 'qc', 'out', '.kit'):
            os.makedirs(sub, exist_ok=True)

    # -- logging / state
    def log(self, *a):
        msg = ' '.join(map(str, a))
        print(msg, flush=True)
        with open('pipe.log', 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + msg + '\n')

    def stamp(self, step):
        return os.path.join('.kit', step + '.done')

    # inputs / outputs per step: a step is up to date when its stamp + outputs exist and are newer than its inputs
    def deps(self, step):
        N = self.num() if os.path.exists('meta.json') else 0
        mp4, srt = f'ep{N:02d}.mp4', f'ep{N:02d}.srt'
        eng = os.path.join(KIT, 'engine', 'engine.js')
        D = {
            'build': (['build.py'], ['script.json', 'scenes.json', 'meta.json']),
            'tts': (['script.json'], ['voice/dur.json']),
            'timeline': (['script.json', 'scenes.json', 'meta.json', 'voice/dur.json', 'pace.json', eng], ['film/timeline.js', 'cues.json']),
            'layout': (['film/timeline.js'], ['qc/layout.txt']),
            'render': (['film/timeline.js', 'film/main.js'], ['out/video.mp4']),
            'mix': (['film/timeline.js', 'voice/dur.json'], ['out/mix_lim.wav']),
            'mux': (['out/video.mp4', 'out/mix_lim.wav'], [mp4]),
            'master': ([self.stamp('mux')], [mp4]),
            'srt': (['cues.json'], [srt]),
            'md': (['cues.json', 'scenes.json'], ['script.md']),
            'qc': ([self.stamp('master')], ['qc/sync.json']),
            'yt': (['cues.json', 'meta.json'], ['youtube.json']),
        }
        return D.get(step, ([], []))

    def up_to_date(self, step):
        ins, outs = self.deps(step)
        st = self.stamp(step)
        if not os.path.exists(st) or not all(os.path.exists(o) for o in outs):
            return False
        t = os.path.getmtime(st)
        return all(os.path.getmtime(i) <= t for i in ins if os.path.exists(i))

    def run(self, steps, explicit):
        for st in steps:
            if st == 'build' and not os.path.exists('build.py'):
                if os.path.exists('script.json'):
                    self.log('[build] no build.py, using existing script.json / scenes.json / meta.json'); continue
                sys.exit('episode needs build.py (or script.json + scenes.json + meta.json)')
            if st != 'tts' and not (explicit or self.a.force) and self.up_to_date(st):
                self.log(f'[{st}] up to date, skipped'); continue
            t0 = time.time(); self.log(f'===== [{st}] start')
            getattr(self, 'step_' + st)()
            wt(self.stamp(st), time.strftime('%Y-%m-%d %H:%M:%S'))
            self.log(f'===== [{st}] done in {time.time() - t0:.0f}s')

    # -- data
    def S(self): return rj('script.json')
    def meta(self): return rj('meta.json')
    def num(self): return int(self.meta()['num'])
    def tl(self):
        s = rt('film/timeline.js')
        L = json.loads(s.split('window.LINES=')[1].split(';\nwindow.SCENES')[0])
        DUR = float(s.split('window.DUR=')[1].split(';')[0])
        return L, DUR

    @staticmethod
    def say(l): return l.get('say') or l['text']

    # ------------------------------------------------------------ build
    def step_build(self):
        env = dict(os.environ, PYTHONPATH=os.path.join(KIT, 'kit') + os.pathsep + os.environ.get('PYTHONPATH', ''), PYTHONUTF8='1')
        before = {f: (rt(f), os.path.getmtime(f)) for f in ('script.json', 'scenes.json', 'meta.json', 'lines.json') if os.path.exists(f)}
        r = subprocess.run([sys.executable, 'build.py'], env=env)
        if r.returncode:
            sys.exit('build.py failed (see the error above)')
        for f in ('script.json', 'scenes.json', 'meta.json', 'lines.json'):
            if f in before and os.path.exists(f) and rt(f) == before[f][0]:
                os.utime(f, (before[f][1], before[f][1]))   # unchanged content: keep old mtime so tts/render are not redone
        for f in ('script.json', 'scenes.json', 'meta.json'):
            if not os.path.exists(f):
                sys.exit(f'build.py did not write {f}: does it end with ep.save(".")?')

    # ------------------------------------------------------------ tts
    def chunks(self, S, limit=380):
        out, order = [], []
        for l in S:
            if l['sc'] not in order: order.append(l['sc'])
        for sc in order:
            L = [l for l in S if l['sc'] == sc]; cur, n = [], 0
            for l in L:
                if cur and n + len(self.say(l)) > limit:
                    out.append(cur); cur, n = [], 0
                cur.append(l); n += len(self.say(l))
            out.append(cur)
        return out

    def step_tts(self):
        from kit import tts_openrouter as T
        from kit.sil_split import split as sil_split
        S = self.S()
        tag = f'{T.DEFAULT_MODEL}|{T.DEFAULT_VOICE}|{T.DEFAULT_INS}'
        h = lambda s: hashlib.sha1((tag + '\n' + s).encode('utf-8')).hexdigest()[:16]
        mf = 'voice/manifest.json'; man = rj(mf, {})
        cp = 'voice/costs.json'; costs = rj(cp, {})
        os.makedirs('voice/scenes', exist_ok=True)

        def ok(l):
            w = f"voice/{l['id']}.wav"
            if not os.path.exists(w): return False
            if l['id'] not in man:  # wav made by an older pipeline: adopt it
                man[l['id']] = h(self.say(l)); return True
            return man[l['id']] == h(self.say(l))

        def synth(text, out, key):
            g = T.synth(text, out, T.DEFAULT_MODEL, T.DEFAULT_VOICE, T.DEFAULT_INS)
            costs[key] = T.cost(g); wj(cp, costs); return costs[key]

        def per_line(L):
            for l in L:
                o = f"voice/{l['id']}.wav"
                synth(self.say(l), o + '.tmp.wav', 'line:' + h(self.say(l))); T.trim(o + '.tmp.wav', o); os.remove(o + '.tmp.wav')
                man[l['id']] = h(self.say(l)); wj(mf, man)

        mode = self.a.tts_mode
        for L in self.chunks(S):
            if all(ok(l) for l in L): continue
            outs = [f"voice/{l['id']}.wav" for l in L]
            if mode == 'line':
                per_line([l for l in L if not ok(l)]); continue
            text = '\n'.join(self.say(l) for l in L); key = h(text)
            sw = f'voice/scenes/{key}.wav'; done = False
            for attempt in range(2):
                if not os.path.exists(sw):
                    c = synth(text, sw, 'scene:' + key); self.log(f"  {L[0]['sc']}: {len(L)} lines, cost US${c}")
                if len(L) == 1:
                    T.trim(sw, outs[0]); done = True; break
                r, conf = sil_split(sw, [self.say(l) for l in L], outs)          # 1) pauses, no ASR (fast)
                self.log(f"  {L[0]['sc']}: pause split confident={conf}")
                if conf: done = True; break
                try:                                                           # 2) Whisper word timestamps
                    from kit.whisper_util import model
                    from kit.whisper_align import split_scene
                    r, _ = split_scene(model('small'), sw, [self.say(l) for l in L], outs)
                    ms = [x['match'] for x in r]; self.log(f"  {L[0]['sc']}: whisper match {ms}")
                    if min(ms) >= 0.5: done = True; break
                except RuntimeError as e:
                    self.log(f"  {L[0]['sc']}: whisper align failed: {str(e)[:100]}")
                os.replace(sw, sw[:-4] + f'.lowconf{attempt}.wav')            # regenerate once
            if not done:                                                       # 3) one request per line
                self.log(f"  {L[0]['sc']}: falling back to per-line synthesis"); per_line(L); continue
            for l in L: man[l['id']] = h(self.say(l))
            wj(mf, man)
        wj(mf, man)
        dur = {}
        for l in S:
            with wave.open(f"voice/{l['id']}.wav") as w:
                dur[l['id']] = round(w.getnframes() / w.getframerate(), 3)
        wj('voice/dur.json', dur)
        tot = sum(v or 0 for v in costs.values())
        self.log('TTS: speech %.1fs, total cost so far US$%.4f' % (sum(dur.values()), tot))

    # ------------------------------------------------------------ timeline
    def step_timeline(self):
        S = self.S(); meta = self.meta(); N = self.num()
        if os.path.exists('voice/dur.json'):
            dur = rj('voice/dur.json')
        else:
            self.log('[timeline] no voice/dur.json yet: estimating durations (4.75 chars/s)')
            dur = {l['id']: len(self.say(l)) / 4.75 for l in S}
        PC = rj('pace.json', {}); LG = PC.get('line', 0.7); SG = PC.get('scene', 1.2)
        t = 1.2; prev = None; cues = []; L2 = []
        for l in S:
            if prev is not None and l['sc'] != prev: t += SG
            t0 = round(t, 3); t1 = round(t0 + dur[l['id']], 3)
            L2.append(dict(id=l['id'], sc=l['sc'], text=l['text'], t0=t0, t1=t1)); cues.append(dict(t0=t0, t1=t1, text=l['text']))
            t = t1 + LG + (l.get('gap') or 0); prev = l['sc']
        DUR = round(L2[-1]['t1'] + 2.5, 2)
        os.makedirs('film', exist_ok=True)
        sc = rj('scenes.json')
        em = dict(head=meta.get('head') or f"EP{N:02d} · {meta['title']}", accent=meta.get('accent', 'A'))
        wt('film/timeline.js', 'window.LINES=' + json.dumps(L2, ensure_ascii=False) + ';\nwindow.SCENES=' + json.dumps(sc, ensure_ascii=False)
           + ';\nwindow.EPMETA=' + json.dumps(em, ensure_ascii=False) + f';\nwindow.DUR={DUR};\n')
        shutil.copyfile(os.path.join(KIT, 'engine', 'engine.js'), 'film/main.js')
        wt('film/index.html', '<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/fonts/fonts.css">'
           '<style>html,body{margin:0;background:#0f1115;overflow:hidden}canvas{display:block}</style></head>\n'
           '<body><canvas id="c" width="1920" height="1080"></canvas><script src="timeline.js"></script><script src="main.js"></script></body></html>\n')
        wj('cues.json', cues)
        self.log('timeline: %.1fs (%.1f min), %d lines, %d scenes' % (DUR, DUR / 60, len(L2), len(sc)))

    def node(self, script, *args, env=None):
        need('node')
        return subprocess.run(['node', os.path.join(KIT, 'render', script), *args], cwd=KIT, env=env)

    def step_layout(self):
        need('node')
        r = subprocess.run(['node', os.path.join(KIT, 'render', 'layout.mjs'), os.path.join(self.d, 'film')], cwd=KIT,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        wt('qc/layout.txt', r.stdout + r.stderr)
        last = (r.stdout.strip().splitlines() or [r.stderr[-300:]])[-1]
        self.log('layout:', last, '(details: qc/layout.txt)')
        if r.returncode:
            sys.exit('layout check could not open the page; see qc/layout.txt')

    def step_stills(self):
        L, _ = self.tl(); last = {}
        for l in L: last[l['sc']] = l['t1']
        ts = [str(round(v - 0.3, 2)) for v in last.values()]
        r = self.node('still.mjs', os.path.join(self.d, 'film'), *ts, '--out', os.path.join(self.d, 'qc', 'pre'), '--prefix', 's_')
        if r.returncode: sys.exit('stills failed')

    # ------------------------------------------------------------ render
    def step_render(self):
        need('ffmpeg')
        wk = self.a.workers or auto_workers()
        env = dict(os.environ)
        if self.a.nvenc:
            env['KIT_VCODEC'] = 'nvenc'
            if wk > 5: self.log('[render] note: consumer GeForce drivers allow a limited number of NVENC sessions (5-8); if render fails, use --workers 5')
        self.log(f'[render] workers={wk} codec={"h264_nvenc" if self.a.nvenc else "libx264"}')
        r = self.node('video.mjs', os.path.join(self.d, 'film'), '--fps', '30', '--workers', str(wk), '--out', os.path.join(self.d, 'out', 'video.mp4'), env=env)
        if r.returncode: sys.exit('render failed (message above). Tips: README 疑難排解')

    # ------------------------------------------------------------ audio
    def step_mix(self):
        import numpy as np, soundfile as sf
        L2, DUR = self.tl(); sr = 24000
        buf = np.zeros(int(DUR * sr) + sr, dtype=np.float32)
        for l in L2:
            a, r = sf.read(f"voice/{l['id']}.wav", dtype='float32')
            if a.ndim > 1: a = a.mean(axis=1)
            if r != sr: sys.exit(f"voice/{l['id']}.wav is {r} Hz; expected 24000")
            i = int(l['t0'] * sr); buf[i:i + len(a)] += a[:len(buf) - i]
        sf.write('out/mix.wav', buf[:int(DUR * sr)], sr)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', 'out/mix.wav', '-af',
                        'alimiter=limit=0.5:attack=5:release=50:level=disabled', 'out/mix_lim.wav'], check=True)

    def vcodec(self, crf):
        if self.a.nvenc:
            return ['-c:v', 'h264_nvenc', '-preset', 'p6', '-tune', 'hq', '-rc', 'vbr', '-cq', str(crf + 1), '-b:v', '0', '-profile:v', 'high']
        return ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf)]

    @staticmethod
    def ffdur(p):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True)
        try: return float(r.stdout.strip().splitlines()[0])
        except Exception: return 0.0

    @staticmethod
    def loud(p):
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
        I = re.findall(r'I:\s+(-?[\d.]+) LUFS', r); P = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)
        return (float(I[-1]) if I else None, float(P[-1]) if P else None)

    def step_mux(self):
        """Port of lemo-opuscar core/render/mux.sh: two-pass loudnorm to -14 LUFS / TP -1.2, pad audio to picture, 30 fps yuv420p."""
        need('ffmpeg'); N = self.num(); V, A, O = 'out/video.mp4', 'out/mix_lim.wav', f'ep{N:02d}.mp4'
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', A, '-af', 'loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr)
        J = json.loads(m.group(0)) if m else {}
        keys = ['input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset']
        if J and all(re.match(r'^-?[\d.]+$', str(J.get(k, ''))) for k in keys):
            LN = ('loudnorm=I=-14:TP=-1.2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:'
                  'measured_thresh={input_thresh}:offset={target_offset}:linear=true').format(**J)
        else:
            LN = 'anull'; self.log('[mux] warning: audio is silent or unreadable by loudnorm; normalisation skipped')
        VD, AD = self.ffdur(V), self.ffdur(A)
        PAD = f',apad=whole_dur={VD}' if AD and VD and AD < VD - 0.02 else ''
        tmp = 'out/mux_tmp.mp4'
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', V, '-i', A, '-filter_complex', f'[0:v]fps=30,format=yuv420p[v];[1:a]{LN},aresample=48000{PAD}[a]',
               '-map', '[v]', '-map', '[a]', *self.vcodec(19), '-r', '30', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', tmp]
        subprocess.run(cmd, check=True); os.replace(tmp, O)
        I, P = self.loud(O); self.log(f'[mux] {O}: {I} LUFS, true peak {P} dBFS')
        if I is not None and (I < -15 or I > -13 or (P or 0) > -1):
            self.log('[mux] warning: missed -14 LUFS / -1.2 dBTP target (the master step usually fixes small misses)')

    def step_master(self):
        need('ffmpeg'); mp = f'ep{self.num():02d}.mp4'; tmp = 'out/master_tmp.mp4'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', mp, '-c:v', 'copy', '-af',
                        'volume=0.35dB,aresample=96000,alimiter=limit=0.8:attack=2:release=50:level=disabled,aresample=48000',
                        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', tmp], check=True)
        I, P = self.loud(tmp); os.replace(tmp, mp)
        self.log(f'[master] {mp}: {I} LUFS, true peak {P} dBFS')
        wj('qc/loudness.json', dict(lufs=I, true_peak=P))

    # ------------------------------------------------------------ text outputs
    def step_srt(self):
        cues = sorted(rj('cues.json'), key=lambda c: c['t0'])
        for k in range(len(cues) - 1): cues[k]['t1'] = min(cues[k]['t1'], cues[k + 1]['t0'])
        def f(s):
            ms = int(round(max(0, s) * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
        wt(f'ep{self.num():02d}.srt', '\n'.join(f"{k + 1}\n{f(c['t0'])} --> {f(c['t1'])}\n{c['text']}\n" for k, c in enumerate(cues)))

    @staticmethod
    def fmt(s):
        s = int(s); return f'{s // 60}:{s % 60:02d}' if s < 3600 else f'{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}'

    def step_md(self):
        S = self.S(); meta = self.meta(); N = self.num(); sc = rj('scenes.json'); cues = rj('cues.json'); _, dur = self.tl()
        out = [f"# EP{N:02d} {meta['title']} — 腳本\n",
               f"- 長度：{self.fmt(dur)}｜旁白：OpenRouter Gemini TTS（{os.environ.get('KIT_TTS_VOICE', 'Enceladus')}）｜字幕：燒錄繁中＋另附 ep{N:02d}.srt",
               "- 括號 [mm:ss] 為該句在成片中的開始時間；「（停頓 n 秒）」為留給觀眾思考的空白。\n"]
        for i, s in enumerate(sc):
            out.append(f"## {i:02d}. {s.get('title') or s.get('chapter')}\n")
            out.append(f"**畫面**：{s.get('desc') or '—'}  \n**講義**：{s.get('ref') or '—'}\n")
            for l, c in zip(S, cues):
                if l['sc'] == s['id']:
                    out.append(f"- [{self.fmt(c['t0'])}] {l['text']}" + (f"（停頓 {l['gap']:.0f} 秒）" if l.get('gap') else ''))
            out.append('')
        wt('script.md', '\n'.join(out))

    def step_qc(self):
        import opencc
        from kit.whisper_util import model
        cc = opencc.OpenCC('s2t'); _, dur = self.tl(); cues = rj('cues.json'); mp = f'ep{self.num():02d}.mp4'
        for i, f in enumerate((0.03, 0.15, 0.28, 0.4, 0.52, 0.64, 0.77, 0.9)):
            t = round(dur * f, 1)
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', mp, '-frames:v', '1', '-q:v', '3', f'qc/f{i}_{int(t)}.jpg'], check=True)
        m = model('small'); res = []
        picks = sorted({min(range(len(cues)), key=lambda k: abs(cues[k]['t0'] - dur * f)) for f in (0.2, 0.5, 0.8)})
        for k in picks:
            c = cues[k]; ss = max(0.0, c['t0'] - 1.0); lead = c['t0'] - ss
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(ss), '-t', str(c['t1'] - c['t0'] + lead + 1.0), '-i', mp,
                            '-ac', '1', '-ar', '16000', 'qc/sync.wav'], check=True)
            words = []
            for kw in (dict(initial_prompt='以下是繁體中文的句子。'), dict(vad_filter=True), dict(vad_filter=False)):
                segs, _ = m.transcribe('qc/sync.wav', language='zh', word_timestamps=True, condition_on_previous_text=False, **kw)
                words = [w for s in segs for w in (s.words or [])]
                if words: break
            hyp = cc.convert(''.join(w.word for w in words))
            st = round(float(words[0].start) - lead, 2) if words else None
            sim = difflib.SequenceMatcher(None, re.sub(r'\W', '', c['text']), re.sub(r'\W', '', hyp)).ratio()
            res.append(dict(t=c['t0'], text=c['text'], heard=hyp, similarity=round(sim, 2), start_offset_s=st))
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,width,height,r_frame_rate',
                            '-of', 'json', mp], capture_output=True, text=True)
        wj('qc/sync.json', dict(sync=res, probe=json.loads(r.stdout or '{}')), indent=1)
        self.log('[qc] sync (similarity, start offset s):', [(x['similarity'], x['start_offset_s']) for x in res], '-> qc/sync.json, frames qc/f*.jpg')

    def starts(self):
        L2, _ = self.tl(); order = []; first = {}
        for l in L2:
            if l['sc'] not in first: first[l['sc']] = l['t0']; order.append(l['sc'])
        return [(s, 0 if i == 0 else first[s] - 0.9) for i, s in enumerate(order)]

    def step_yt(self):
        meta = self.meta(); N = self.num(); sc = {s['id']: s for s in rj('scenes.json')}
        ch = '\n'.join(f"{self.fmt(t)} {sc[s].get('chapter') or sc[s].get('title')}" for s, t in self.starts())
        series = meta.get('series', '機器學習從零開始')
        about = meta.get('about', '「機器學習從零開始」是一套給完全新手的機器學習補習影片，內容依照大學「機器學習」課程講義整理，'
                                  '用白話、生活例子和手算例題，一步一步帶你看懂。\n旁白為 AI 合成語音，畫面為程式生成的圖解（無 AI 生成影像）。')
        desc = meta['summary'] + '\n\n章節\n' + ch + '\n\n' + about
        y = dict(title=f"{series} EP{N:02d}｜{meta['title']}", description=desc, tags=meta.get('tags', []), synthetic=True,
                 language='zh-TW', category='Education', video_file=f'ep{N:02d}.mp4', captions_file=f'ep{N:02d}.srt')
        s = json.dumps(y, ensure_ascii=False)
        if re.search(r'[A-Za-z]:\\\\|/home/|/Users/|/workspace|localhost|127\.0\.0\.1|sk-or-', s):
            sys.exit('youtube.json would leak a local path or key; check meta.json')
        wj('youtube.json', y, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('episode_dir')
    ap.add_argument('steps', nargs='*', help='steps to run (default: all). "all" = ' + ' '.join(ALL))
    ap.add_argument('--workers', type=int, default=int(os.environ.get('KIT_WORKERS', '0')) or None,
                    help='parallel render workers (default: auto from CPU/RAM, max 8; env KIT_WORKERS)')
    ap.add_argument('--nvenc', action='store_true', default=os.environ.get('KIT_NVENC') == '1', help='encode with NVIDIA h264_nvenc (env KIT_NVENC=1)')
    ap.add_argument('--whisper-device', choices=['cpu', 'cuda', 'auto'], default=None, help='device for faster-whisper (env KIT_WHISPER_DEVICE, default cpu)')
    ap.add_argument('--tts-mode', choices=['scene', 'line'], default='scene', help='scene = one request per scene (default), line = one per line')
    ap.add_argument('--force', action='store_true', help='re-run steps even if up to date')
    ap.add_argument('--low-priority', action='store_true', help='run below normal CPU priority (keeps the PC usable)')
    a = ap.parse_args()
    load_env(); kit_dirs()
    if a.whisper_device: os.environ['KIT_WHISPER_DEVICE'] = a.whisper_device
    if a.low_priority: low_priority()
    steps = a.steps or ['all']; explicit = steps != ['all']
    if steps == ['all']: steps = ALL
    bad = [s for s in steps if s not in ALL + EXTRA]
    if bad: sys.exit(f'unknown step(s): {bad}. Steps: {" ".join(ALL + EXTRA)}')
    need('ffmpeg'); need('ffprobe')
    t0 = time.time(); ep = Episode(a.episode_dir, a)
    ep.run(steps, explicit)
    ep.log(f'ALL DONE in {(time.time() - t0) / 60:.1f} min -> {ep.d}')


if __name__ == '__main__':
    main()
