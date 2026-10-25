# -*- coding: utf-8 -*-
"""Генерація картинок через HTTP-API ComfyUI (агент 01_IMAGE).

Запуск (будь-який Python 3.9+, лише стандартна бібліотека):
    python gen_images.py              # усі, яких ще немає
    python gen_images.py --ids w_kit,o_apple --force

Сервер має бути піднятий ярликом «Запустити генератор зображень» (порт 8188);
якщо він не відповідає, скрипт піднімає його сам. Готові PNG складаються в
tools/_raw/<id>.png — далі cut_bg.py вирізає фон і зводить до 512×512
в assets/img.

Чому по одній картинці за раз, а не черга з 36: 2026-10-20 у ComfyUI після
дев'яти генерацій поспіль декодування VAE впало в OOM, обробник помилки впав
повторно й заклинив контекст CUDA — сервер лишався живим, але /system_stats
віддавав 500 назавжди (див. CLAUDE.md агентів). Тому тут: /free кожні кілька
картинок, перевірка стану сервера й автоматичний перезапуск із продовженням
з того ж місця.
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.request

# Консоль Windows тут cp1251: будь-який символ поза нею вбиває скрипт просто
# на print (зловив на U+02BC у слові «пам'ять» — упало після восьмої картинки).
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

HOST = '127.0.0.1:8188'
ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, '_raw')
COMFY_OUT = r'G:\LOCAL AI AGENTS\_OUT\images'
COMFY_IN = r'G:\LOCAL AI AGENTS\01_IMAGE\ComfyUI\input'
LAUNCHER = r'G:\LOCAL AI AGENTS\01_IMAGE\Запустити генератор зображень.cmd'
FREE_EVERY = 8
# Скільки шуму додавати поверх взірця в режимі --ref. Менше — ближче до
# взірця, але поза майже не змінюється; більше — нова поза, але інший герой.
REF_DENOISE = 0.62


def api(path, payload=None, timeout=30):
    url = 'http://%s%s' % (HOST, path)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return json.loads(body) if body.strip() else {}


def server_ok():
    try:
        api('/system_stats', timeout=10)
        return True
    except Exception:                                             # noqa: BLE001
        return False


def wait_server(limit=300):
    t0 = time.time()
    while time.time() - t0 < limit:
        if server_ok():
            return True
        time.sleep(3)
    return False


def comfy_pids():
    """PID процесів ComfyUI — шукаємо за командним рядком, не за іменем.

    Шукати за «01_IMAGE» не можна: запускач робить cd у папку ComfyUI й
    викликає `.venv\\Scripts\\python.exe main.py` відносним шляхом, тож
    назви папки в командному рядку немає. Надійна прикмета — main.py
    разом із портом. Процесів два: сам запуск і породжений ним базовий
    інтерпретатор venv — тому вбиваємо обидва.
    """
    ps = ('Get-CimInstance Win32_Process -Filter "Name=\'python.exe\'" | '
          'Where-Object { $_.CommandLine -like \'*main.py*--port 8188*\' } | '
          'Select-Object -ExpandProperty ProcessId')
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command', ps],
                             capture_output=True, text=True, timeout=60).stdout
        return [int(x) for x in out.split()]
    except Exception:                                             # noqa: BLE001
        return []


def start_server():
    subprocess.Popen(['cmd', '/c', 'start', '', LAUNCHER], creationflags=0x00000008)


def restart_server():
    for pid in comfy_pids():
        print('[img] вбиваю заклинений ComfyUI pid=%d' % pid, flush=True)
        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True)
    time.sleep(5)
    print('[img] піднімаю ComfyUI заново...', flush=True)
    start_server()
    return wait_server()


def workflow(img, prompt_text, seed, ref=None, denoise=1.0):
    """Звичайний txt2img, а з ref — той самий граф, але латент не порожній.

    Персонаж із кількох поз інакше не збирається: на текстовий промпт SDXL
    щоразу малює іншого героя, і зміна пози читається як зміна героя. Тут
    за основу береться вже вибрана картинка, і модель лише переписує її на
    задану позу — колір, форма й стиль лишаються ті самі.
    """
    flow = {
        '4': {'class_type': 'CheckpointLoaderSimple',
              'inputs': {'ckpt_name': img['checkpoint']}},
        '10': {'class_type': 'VAELoader',
               'inputs': {'vae_name': img['vae']}},
        '6': {'class_type': 'CLIPTextEncode',
              'inputs': {'text': prompt_text, 'clip': ['4', 1]}},
        '7': {'class_type': 'CLIPTextEncode',
              'inputs': {'text': img['negative'], 'clip': ['4', 1]}},
        '5': {'class_type': 'EmptyLatentImage',
              'inputs': {'width': img['size'][0], 'height': img['size'][1],
                         'batch_size': 1}},
        '3': {'class_type': 'KSampler',
              'inputs': {'seed': seed, 'steps': img['steps'], 'cfg': img['cfg'],
                         'sampler_name': img['sampler'], 'scheduler': img['scheduler'],
                         'denoise': denoise, 'model': ['4', 0], 'positive': ['6', 0],
                         'negative': ['7', 0], 'latent_image': ['5', 0]}},
        # VAEDecodeTiled, а не VAEDecode: саме декодування VAE дає шпиль
        # пам'яті, на якому 2026-10-20 сервер двічі впав в OOM і заклинив
        # контекст CUDA (/system_stats потім назавжди 500). Плитками 512
        # шпиля немає; на 1024×1024 різниці в картинці не видно.
        '8': {'class_type': 'VAEDecodeTiled',
              'inputs': {'samples': ['3', 0], 'vae': ['10', 0],
                         'tile_size': 512, 'overlap': 64,
                         'temporal_size': 64, 'temporal_overlap': 8}},
        '9': {'class_type': 'SaveImage',
              'inputs': {'filename_prefix': 'ostriv/x', 'images': ['8', 0]}},
    }
    if ref:
        flow['11'] = {'class_type': 'LoadImage', 'inputs': {'image': ref}}
        flow['12'] = {'class_type': 'VAEEncode',
                      'inputs': {'pixels': ['11', 0], 'vae': ['10', 0]}}
        flow['3']['inputs']['latent_image'] = ['12', 0]
        del flow['5']
    return flow


def put_ref(path):
    """Кладе взірець туди, де його бачить LoadImage, і вертає ім'я файла."""
    name = 'ostriv_ref_' + os.path.basename(path)
    os.makedirs(COMFY_IN, exist_ok=True)
    shutil.copy2(path, os.path.join(COMFY_IN, name))
    return name


def run_one(img, cid, obj, seed, timeout=300, ref=None, denoise=1.0):
    # Острови (i_*) мають власний промпт: із загальним SDXL малював пейзаж
    # на весь кадр, а на карті острів — іконка 96×96 (див. manifest.json).
    style = img['style_island'] if cid.startswith('i_') else img['style']
    text = style.replace('{object}', obj)
    res = api('/prompt', {'prompt': workflow(img, text, seed, ref, denoise)})
    pid = res['prompt_id']
    t0 = time.time()
    last_check = t0
    while time.time() - t0 < timeout:
        time.sleep(2)
        # Заклинений сервер лишається живим і тримає завдання в «running»
        # вічно — чекати тут повний таймаут марно, швидше перезапустити.
        if time.time() - last_check > 45:
            last_check = time.time()
            if not server_ok():
                raise RuntimeError('сервер заклинило (/system_stats 500)')
        try:
            hist = api('/history/%s' % pid, timeout=20)
        except Exception:                                         # noqa: BLE001
            continue
        if pid not in hist:
            continue
        entry = hist[pid]
        status = entry.get('status', {})
        if status.get('status_str') == 'error':
            raise RuntimeError('ComfyUI: %s' % json.dumps(status)[:400])
        for out in entry.get('outputs', {}).values():
            for im in out.get('images', []):
                src = os.path.join(COMFY_OUT, im.get('subfolder', ''), im['filename'])
                if os.path.exists(src):
                    dst = os.path.join(RAW, cid + '.png')
                    shutil.copy2(src, dst)
                    return dst, time.time() - t0
        if entry.get('outputs'):
            raise RuntimeError('виконано, але файл не знайдено')
    raise TimeoutError('сервер не віддав картинку за відведений час')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', default=os.path.join(ROOT, 'manifest.json'))
    ap.add_argument('--ids', default='')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--seed', type=int, default=20261020)
    ap.add_argument('--reseed', type=int, default=0,
                    help='інший варіант тієї ж картинки: --force --reseed 1')
    ap.add_argument('--ref', default='',
                    help='взірець: шлях до PNG або id з _raw. Нові картинки '
                         'малюються поверх нього — так виходить один і той '
                         'самий герой у різних позах')
    ap.add_argument('--denoise', type=float, default=REF_DENOISE,
                    help='наскільки відходити від взірця (0.5 — майже він, '
                         '0.75 — вже інший герой); діє лише з --ref')
    args = ap.parse_args()

    ref = None
    if args.ref:
        p = args.ref if os.path.exists(args.ref) else os.path.join(RAW, args.ref + '.png')
        if not os.path.exists(p):
            sys.exit('[img] взірця немає: %s' % p)
        ref = put_ref(p)

    with open(args.manifest, encoding='utf-8') as f:
        man = json.load(f)
    img = man['image']
    # Фігури для візерунків малює draw_shapes.py — SDXL на "red circle"
    # видавав песика, а тут потрібен рівний край (див. manifest.json).
    drawn = set(man.get('shapes', {}).get('items', {}))
    drawn |= set(img.get('reuse', {}))      # беруть готову картинку іншого id
    # Ключі на _ — це пояснення в маніфесті, а не id картинки.
    items = {k: v for k, v in img['items'].items()
             if k not in drawn and not k.startswith('_')}
    ids = [i.strip() for i in args.ids.split(',') if i.strip()] or list(items)
    ids = [i for i in ids if i in items]
    os.makedirs(RAW, exist_ok=True)

    if not server_ok():
        print('[img] ComfyUI не відповідає — піднімаю ярликом', flush=True)
        start_server()
        if not wait_server():
            sys.exit('[img] сервер не піднявся за 5 хв — запустіть ярлик вручну')

    todo = [i for i in ids
            if args.force or not os.path.exists(os.path.join(RAW, i + '.png'))]
    print('[img] до роботи %d з %d' % (len(todo), len(ids)), flush=True)
    rnd = random.Random(args.seed + args.reseed * 1009)
    seeds = {i: rnd.randrange(1, 2 ** 31) for i in sorted(items)}

    done = fail = 0
    t_all = time.time()
    for k, cid in enumerate(todo, 1):
        if k > 1 and (k - 1) % FREE_EVERY == 0:
            try:
                api('/free', {'unload_models': True, 'free_memory': True}, timeout=60)
                print('[img] память звільнено', flush=True)
                time.sleep(3)
            except Exception as e:                                # noqa: BLE001
                print('[img] /free не вдалось: %r' % (e,), flush=True)
        ok = False
        for attempt in (1, 2):
            try:
                dst, dt = run_one(img, cid, items[cid], seeds[cid],
                                  ref=ref, denoise=args.denoise if ref else 1.0)
                print('[img] %2d/%d %-14s %5.1f с -> %s' % (k, len(todo), cid, dt, dst),
                      flush=True)
                ok = True
                break
            except Exception as e:                                # noqa: BLE001
                print('[img] %s: спроба %d не вдалась: %r' % (cid, attempt, e), flush=True)
                if not server_ok():
                    if not restart_server():
                        sys.exit('[img] перезапуск ComfyUI не допоміг — зупиняюсь')
        done += 1 if ok else 0
        fail += 0 if ok else 1
    print('[img] готово: %d картинок, збоїв %d, %.1f хв'
          % (done, fail, (time.time() - t_all) / 60), flush=True)


if __name__ == '__main__':
    main()
