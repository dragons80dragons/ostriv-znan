# -*- coding: utf-8 -*-
"""Короткі анімації краба через AnimateDiff у тому самому ComfyUI (порт 8188).

Навіщо: пози окремими картинками SDXL малювати не вміє (див. README) —
модель додає предмет, але не переставляє кінцівки. AnimateDiff малює не
картинку, а послідовність кадрів одразу, тож рух виникає всередині моделі,
а не склеюється з окремих спроб.

Запускати інтерпретатором, у якому є Pillow (агент 11_BGREMOVE) — сам
ComfyUI викликається по HTTP, тут потрібна лише збірка кадрів:

    "G:\\LOCAL AI AGENTS\\11_BGREMOVE\\.venv\\Scripts\\python.exe" gen_crab_anim.py --mood joy

Вихід: tools/_anim/<mood>/0001.png… і готові <mood>.webp та <mood>.gif поряд.
"""
import argparse
import io
import json
import os
import shutil
import sys
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

HOST = '127.0.0.1:8188'
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '_anim')
COMFY_OUT = r'G:\LOCAL AI AGENTS\_OUT\images'
COMFY_IN = r'G:\LOCAL AI AGENTS\01_IMAGE\ComfyUI\input'
# DreamShaper 8, а не ToonYou: та була аніме-моделлю і тягла будь-який
# промпт у бік обличчя — краб виходив симетричною червоною плямою.
CKPT = 'dreamshaper_8.safetensors'
MOTION = 'mm_sd_v15_v2.ckpt'

# Той самий опис персонажа, що й у маніфесті: краб має лишитися тим самим,
# навіть коли модель інша (AnimateDiff — це SD 1.5, а не SDXL).
# Слово «crab» стоїть першим і повторене: перша спроба на аніме-моделі
# дала симетричну червону пляму на обличчя, тож і в негативі прямо
# сказано, чого не малювати. DreamShaper тягне в бік фотографії, тому
# слова про пласку заливку й контур теж важливі.
WHO = ('a crab, one red cartoon crab, full body, round shell, two big '
       'claws, four small legs, big round cartoon eyes, wide smile, '
       'flat vector illustration, children book style, thick black '
       'outline, simple shapes, bright flat colors, no shading, '
       'plain white background')
NEG = ('face, portrait, girl, woman, anime face, human, hair, photo, '
       'realistic, 3d render, shading, gradient, dark, blurry, deformed, '
       'extra limbs, text, watermark, multiple crabs, cluttered '
       'background, symmetrical pattern, blood, splatter')

MOODS = {
    'hi':    'waving one claw hello, standing still',
    'walk':  'walking sideways step by step',
    'joy':   'jumping up and down with both claws raised in joy',
    'clap':  'clapping both claws together',
    'oops':  'shaking its head sadly, claws drooping',
    'point': 'pointing to the side with one claw stretched out',
    'think': 'tilting its head, one claw under its chin',
    'sleep': 'sleeping, breathing slowly, eyes closed',
    'flag':  'waving a small red flag on a stick',
    'star':  'holding a big golden star up high',
    'read':  'reading an open book',
    'swim':  'swimming, bubbles rising around it',
}


def api(path, payload=None, timeout=30):
    url = 'http://%s%s' % (HOST, path)
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def pick_loader(info):
    """Ім'я вузла AnimateDiff залежить від версії розширення, тож питаємо.

    Gen1-завантажувач приймає модель і модуль руху одним вузлом — це все,
    що тут потрібно; старіші версії звуть його інакше.
    """
    for name in ('ADE_AnimateDiffLoaderGen1', 'ADE_AnimateDiffLoaderWithContext',
                 'AnimateDiffLoaderV1', 'ADE_AnimateDiffLoaderV1Advanced'):
        if name in info:
            return name
    found = [k for k in info if 'AnimateDiff' in k and 'Loader' in k]
    if not found:
        sys.exit('[anim] у ComfyUI немає вузлів AnimateDiff — чи встановлено '
                 'custom_nodes/ComfyUI-AnimateDiff-Evolved і чи перезапущено сервер?')
    return found[0]


def loader_inputs(info, name, model_ref):
    """Заповнює обов'язкові входи завантажувача значеннями за списком з сервера.

    Перебирати вручну всі версії розширення марно: сервер сам каже, які
    входи обов'язкові і які значення допустимі.
    """
    spec = info[name]['input'].get('required', {})
    out = {}
    for key, decl in spec.items():
        if key == 'model':
            out[key] = model_ref
            continue
        meta = decl[1] if len(decl) > 1 and isinstance(decl[1], dict) else {}
        # Два формати опису: старий тримав перелік значень першим елементом,
        # новий (ComfyUI 0.4x) пише там рядок "COMBO", а самі значення — у
        # другому словнику під ключем options.
        opts = decl[0] if isinstance(decl[0], list) else meta.get('options')
        if isinstance(opts, list) and opts:
            if key in ('model_name', 'motion_model'):
                out[key] = MOTION if MOTION in opts else opts[0]
            else:
                out[key] = meta.get('default', opts[0])
        elif 'default' in meta:
            out[key] = meta['default']
    return out


def workflow(info, mood, frames, steps, cfg, seed, ref=None, denoise=1.0, motion=1.0):
    loader = pick_loader(info)
    text = MOODS[mood] + ', ' + WHO
    flow = {
        '4': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': CKPT}},
        '6': {'class_type': 'CLIPTextEncode', 'inputs': {'text': text, 'clip': ['4', 1]}},
        '7': {'class_type': 'CLIPTextEncode', 'inputs': {'text': NEG, 'clip': ['4', 1]}},
        '20': {'class_type': loader, 'inputs': loader_inputs(info, loader, ['4', 0])},
        # effect_multival — сила руху модуля. Перша проба дала кадри, де
        # клешні ледь ворушаться; цим важелем рух можна підсилити.
        '3': {'class_type': 'KSampler',
              'inputs': {'seed': seed, 'steps': steps, 'cfg': cfg,
                         'sampler_name': 'euler', 'scheduler': 'normal',
                         'denoise': denoise, 'model': ['20', 0],
                         'positive': ['6', 0], 'negative': ['7', 0],
                         'latent_image': ['5', 0]}},
        '8': {'class_type': 'VAEDecode', 'inputs': {'samples': ['3', 0], 'vae': ['4', 2]}},
        '9': {'class_type': 'SaveImage',
              'inputs': {'filename_prefix': 'crab/%s' % mood, 'images': ['8', 0]}},
    }
    if motion != 1.0 and 'ADE_MultivalDynamic' in info:
        flow['21'] = {'class_type': 'ADE_MultivalDynamic',
                      'inputs': {'float_val': motion}}
        flow['20']['inputs']['effect_multival'] = ['21', 0]
    if ref:
        # Усі кадри починаються з нашої картинки: герой лишається тим самим,
        # а рух дає модуль руху, а не промпт.
        flow['11'] = {'class_type': 'LoadImage', 'inputs': {'image': ref}}
        flow['12'] = {'class_type': 'VAEEncode',
                      'inputs': {'pixels': ['11', 0], 'vae': ['4', 2]}}
        flow['13'] = {'class_type': 'RepeatLatentBatch',
                      'inputs': {'samples': ['12', 0], 'amount': frames}}
        flow['3']['inputs']['latent_image'] = ['13', 0]
    else:
        flow['5'] = {'class_type': 'EmptyLatentImage',
                     'inputs': {'width': 512, 'height': 512, 'batch_size': frames}}
    return flow


def run(flow, mood, timeout=1800):
    res = api('/prompt', {'prompt': flow})
    pid = res['prompt_id']
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        try:
            hist = api('/history/%s' % pid, timeout=20)
        except Exception:                                         # noqa: BLE001
            continue
        if pid not in hist:
            continue
        entry = hist[pid]
        if entry.get('status', {}).get('status_str') == 'error':
            raise RuntimeError(json.dumps(entry['status'])[:600])
        files = []
        for out in entry.get('outputs', {}).values():
            for im in out.get('images', []):
                files.append(os.path.join(COMFY_OUT, im.get('subfolder', ''), im['filename']))
        if files:
            return files, time.time() - t0
    raise TimeoutError('сервер не віддав кадри за відведений час')


def assemble(files, mood, fps):
    from PIL import Image
    dst = os.path.join(OUT, mood)
    os.makedirs(dst, exist_ok=True)
    frames = []
    for i, f in enumerate(sorted(files), 1):
        p = os.path.join(dst, '%04d.png' % i)
        shutil.copy2(f, p)
        frames.append(Image.open(p).convert('RGB'))
    ms = int(round(1000.0 / fps))
    webp = os.path.join(OUT, '%s.webp' % mood)
    gif = os.path.join(OUT, '%s.gif' % mood)
    frames[0].save(webp, save_all=True, append_images=frames[1:],
                   duration=ms, loop=0, quality=80, method=4)
    frames[0].save(gif, save_all=True, append_images=frames[1:],
                   duration=ms, loop=0, optimize=True)
    return webp, gif, len(frames)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mood', default='joy', help='через кому або "all"')
    ap.add_argument('--frames', type=int, default=16)
    ap.add_argument('--fps', type=int, default=8)
    ap.add_argument('--steps', type=int, default=20)
    ap.add_argument('--cfg', type=float, default=8.0)
    ap.add_argument('--seed', type=int, default=20261025)
    ap.add_argument('--ref', default='', help='PNG-взірець: кадри почнуться з нього')
    ap.add_argument('--denoise', type=float, default=0.75, help='лише з --ref')
    ap.add_argument('--ckpt', default=CKPT, help='інша базова модель SD 1.5')
    ap.add_argument('--tag', default='', help='суфікс до назви файлів: дві проби поруч')
    ap.add_argument('--motion', type=float, default=1.0,
                    help='сила руху модуля: 1.0 звичайна, 1.4 помітніша')
    args = ap.parse_args()
    globals()['CKPT'] = args.ckpt

    os.makedirs(OUT, exist_ok=True)
    ref = None
    if args.ref:
        # Взірець обов'язково зводимо до 512: він лежить у 1024, а кадрів
        # шістнадцять — на 1024 це вчетверо більше пікселів і прямий шлях
        # в OOM, на якому ComfyUI уже клинило (див. gen_images.py).
        from PIL import Image
        os.makedirs(COMFY_IN, exist_ok=True)
        ref = 'crab_ref_512.png'
        # Картинки в грі прозорі. Просте convert('RGB') робить прозоре
        # чорним — і модель фарбує в чорне весь кадр. Підкладаємо біле,
        # бо саме на білому цього краба й намалювали.
        src = Image.open(args.ref).convert('RGBA')
        flat = Image.new('RGBA', src.size, (255, 255, 255, 255))
        flat.alpha_composite(src)
        flat.convert('RGB').resize((512, 512), Image.LANCZOS).save(
            os.path.join(COMFY_IN, ref))

    info = api('/object_info', timeout=120)
    print('[anim] вузол AnimateDiff: %s' % pick_loader(info), flush=True)

    moods = list(MOODS) if args.mood == 'all' else [m.strip() for m in args.mood.split(',')]
    for m in moods:
        if m not in MOODS:
            print('[anim] невідомий настрій: %s' % m, flush=True)
            continue
        flow = workflow(info, m, args.frames, args.steps, args.cfg, args.seed,
                        ref, args.denoise if ref else 1.0, args.motion)
        try:
            files, dt = run(flow, m)
        except Exception as e:                                    # noqa: BLE001
            print('[anim] %-6s збій: %r' % (m, e), flush=True)
            continue
        webp, gif, n = assemble(files, m + args.tag, args.fps)
        print('[anim] %-6s %d кадрів за %.0f с -> %s'
              % (m + args.tag, n, dt, os.path.basename(webp)), flush=True)


if __name__ == '__main__':
    main()
