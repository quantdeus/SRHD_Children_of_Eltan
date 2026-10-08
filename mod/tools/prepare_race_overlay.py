#!/usr/bin/env python3
"""Prepare an opt-in source overlay for a pinned team checkout; never install it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

SPEC = Path(__file__).resolve().parents[1] / 'experiments' / 'race_overlay'
RSON = 'src/scripts/CE_MapSmoke.rson'
MAIN = 'src/config/CE_MapSmoke.Main.txt'
LANG = 'src/config/CE_MapSmoke.Lang.txt'
TRANSIT = 'src/config/CE_InterarmTransit.Lang.txt'


def call(name: str) -> str:
    return f"ExecuteCodeFromString(GenerateCodeStringFromBlock('CE.RaceOverlay.{name}'));"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f'Expected one integration point: {old!r}')
    return text.replace(old, new, 1)


def lang_fragment() -> str:
    names = ['Малок', 'Пеленг', 'Человек', 'Фэянин', 'Гаалец',
             'Стронг', 'Агилл', 'Медиум', 'Интелл', 'Мензол']
    lines = ['CE ^{', '    RaceOverlay ^{',
             '        BaseOnly=Сменить расу можно на пиратской базе.',
             '        Confirm=Подтвердить смену расы: ',
             '        Selected=Текущая раса: ',
             '        CaptureFailed=Не удалось сохранить личность для перехода. Проверьте выбор расы на базе.',
             '        InvalidTransfer=Данные личности повреждены или отсутствуют. Загрузите сохранение перед переходом.',
             '        Menu0=Старый рукав: 1 - Малок; 2 - Пеленг; 3 - Человек; 4 - Фэянин; 5 - Гаалец.',
             '        Menu1=Второй Дом: 1 - Стронг; 2 - Агилл; 3 - Медиум; 4 - Интелл; 5 - Мензол.',
             '        Names ^{']
    lines += [f'            {i}={name}' for i, name in enumerate(names, 1)]
    lines += ['        }']
    for name in ['Ensure', 'Refresh', 'Menu', 'Capture', 'Restore']:
        lines.append(f'        {name} ^{{')
        # Repeated zero keys are the same BlockPar code representation used by
        # the team. Braces belong to the code value, not to BlockPar child nodes.
        lines += ['            0=' + line for line in
                  (SPEC / f'{name}.code').read_text(encoding='utf-8').splitlines()]
        lines.append('        }')
    lines += ['    }', '}', 'ShipInfo ^{', '    AddInfo ^{', '        CustomInfos ^{',
              '            CE_RaceIdentity ^{',
              '                Description=Происхождение: <TextData1>. Текущая раса: <TextData2>.',
              '            }', '        }', '    }', '}', '']
    return '\n'.join(lines)


def prepare(team: Path, output: Path | None = None) -> dict:
    manifest = json.loads((SPEC / 'upstream.json').read_text(encoding='utf-8'))
    raw = {}
    for rel, digest in manifest['files'].items():
        content = (team / rel).read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f'Upstream changed: {rel}; re-audit integration points first')
        raw[rel] = content
    tree = json.loads(raw[RSON])
    operations = [op for group in tree['Visual.Objects']
                  for op in group.get('Operations', []) if op.get('Name') == 'Adapter smoke']
    if len(operations) != 1:
        raise ValueError('Expected one Adapter smoke operation')
    operation = operations[0]
    code = '\n'.join(operation['Code'])
    # Arrival runs before the ordinary ensure hook: do not derive origin from
    # the destination save captain and then mistake it for the traveller.
    for clear in ['ceClearStash();', 'ceClearStashR();']:
        code = replace_once(code, clear, call('Restore') + '\n    ' + clear)
    code += '\n' + call('Ensure')
    operation['Code'] = code.splitlines()
    operation['Total.Lines'] = len(operation['Code'])
    transit = raw[TRANSIT].decode('utf-8')
    capture = ("ExecuteCodeFromString(GenerateCodeStringFromBlock('CE.RaceOverlay.Capture')); "
               "unknown ceRaceFetch=ImportedFunction('CESecondMapAdapter','CEAdapterFetchPlayerValue'); "
               "if(ceRaceFetch(17)!=1128616497) { MessageBox(CT('CE.RaceOverlay.CaptureFailed')); exit; }")
    transit = replace_once(transit, '24=ceSaveStash();',
                           '24=' + capture + '\n                    24=ceSaveStash();')
    products = {
        RSON: json.dumps(tree, ensure_ascii=False, indent=2) + '\n',
        MAIN: raw[MAIN].decode('utf-8') + '\n' + (SPEC / 'UI.Main.txt').read_text(encoding='utf-8'),
        LANG: raw[LANG].decode('utf-8') + '\n' + lang_fragment(),
        TRANSIT: transit,
    }
    for rel, content in products.items():
        content.encode('cp1251', errors='strict')
    report = {'status': 'source-overlay-only', 'team_commit': manifest['commit'],
              'rscript_compiled': False, 'game_tested': False,
              'stash_slots': list(range(17, 23)),
              'files': {p: hashlib.sha256(s.encode('utf-8')).hexdigest()
                        for p, s in products.items()}}
    if output is not None:
        output = output.resolve()
        team = team.resolve()
        if output == team or team in output.parents or output in team.parents:
            raise ValueError('Output must be separate from team checkout')
        if output.exists():
            raise ValueError('Output already exists; choose a fresh directory')
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='ce-race-', dir=output.parent))
        try:
            for rel, content in products.items():
                target = staging / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding='utf-8', newline='\n')
            (staging / 'race-overlay-report.json').write_text(
                json.dumps(report, indent=2) + '\n', encoding='utf-8')
            staging.rename(output)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--team', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='Write source files to a NEW directory; default: audit only')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.team, args.output), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
