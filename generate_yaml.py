import os
from jinja2 import Environment, FileSystemLoader

prefixes = [
    'wb1',
    'wb2'
]

SRC_DIR = 'src'
TEMPLATE_DIR = 'build/templates'
TEMPLATE_FILES = [
    'globals.j2',
    'sensors.j2',
    'binary_sensors.j2',
    'outputs.j2',
    'lights.j2',
]
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Генерация Jinja2 шаблонов из исходников в src/
for filename in TEMPLATE_FILES:
    src_path = os.path.join(SRC_DIR, filename.replace('.j2', '.yaml'))
    template_path = os.path.join(TEMPLATE_DIR, filename.replace('.yaml', '.j2'))
    with open(src_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    header = lines[0] if lines else ''
    body = ''.join(lines[1:])
    body = body.replace('wb1', '{{ prefix }}').replace('ch1', 'ch{{ ch }}')
    jinja_block = f'{header}{{% for ch in range(1, 5) %}}\n{body}{{% endfor %}}\n'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(jinja_block)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_template(template_name, context):
    template = env.get_template(template_name)
    return template.render(context)


with open('src/main.yaml', 'r', encoding='utf-8') as f:
    base_main = f.read()

# Сначала генерируем все файлы по шаблонам
for prefix in prefixes:
    build_dir = os.path.join('build', prefix)
    os.makedirs(build_dir, exist_ok=True)
    for tmpl in TEMPLATE_FILES:
        name = tmpl.replace('.j2', '.yaml')
        output_path = os.path.join(build_dir, name)
        rendered = render_template(tmpl, {'prefix': prefix})
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
    print(f"🔧 Генерация конфигов для {prefix}")

# Затем собираем финальный esp_generated.yaml
with open('esp_generated.yaml', 'w', encoding='utf-8') as f_out:
    f_out.write(base_main + '\n')

    for tmpl in TEMPLATE_FILES:
        name = tmpl.replace('.j2', '.yaml')
        section = name.split('.')[0]

        for i, prefix in enumerate(prefixes):
            path = os.path.join('build', prefix, name)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # для первого блока сохраняем тег (первая строка), для остальных — пропускаем
            if i == 0:
                f_out.write(''.join(lines) + '\n')
            else:
                f_out.write(''.join(lines[1:]) + '\n')

print(f"🔧 Done")
