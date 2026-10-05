#!/usr/bin/env python3
"""Generate the six static pages from Italian templates and translation catalogs."""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / 'site/config.json').read_text())
ORIGIN = CONFIG['origin'].rstrip('/')
if urlsplit(ORIGIN).scheme != 'https' or not urlsplit(ORIGIN).netloc or urlsplit(ORIGIN).path:
    raise ValueError('origin must be an HTTPS origin without a path')
LANGUAGES = ('en', 'it', 'es')
NAMES = {'en': 'English', 'it': 'Italiano', 'es': 'Español'}
LABELS = {'en': 'Choose language', 'it': 'Scegli lingua', 'es': 'Elegir idioma'}
MESSAGES = {
    'en': ('Information about the JOIA project', 'Hello! I would like information about the JOIA project.'),
    'it': ('Informazioni sul progetto JOIA', 'Ciao! Vorrei ricevere informazioni sul progetto JOIA.'),
    'es': ('Información sobre el proyecto JOIA', '¡Hola! Me gustaría recibir información sobre el proyecto JOIA.'),
}
UNTRANSLATED = {'JOIA Pizza Bar', 'JOIA', 'Pasta Bar', 'JOIA Tenerife Pizza Bar', 'Italian soul. Mediterranean spirit.',
                'Italian soul.', 'Mediterranean spirit.', 'Italian pasta. Joia style.',
                'The joy of pizza', 'The joy of pizza.', 'THE JOY', 'of', 'PIZZA',
                '01 / JOIA', 'I.', 'II.', 'III.', '01', '02', '03', '©', '2026', '↗', '↑', '✳',
                'info@joia-pizzeria.com'}


def route(lang, page):
    return ('/' if lang == 'en' else f'/{lang}/') + ('' if page == 'home' else 'partner.html')


def translate(source, lang, page):
    if lang == 'it':
        return source
    catalog = json.loads((ROOT / f'site/translations/{lang}.json').read_text())
    def lookup(value):
        key = html.unescape(value.strip())
        if not key or key in UNTRANSLATED:
            return value
        if key not in catalog:
            raise ValueError(f'Missing {lang} translation in {page}: {key}')
        replacement = catalog[key]
        if page == 'partner' and lang == 'es' and key == 'insieme.':
            replacement = 'juntos.'
        return value[:len(value)-len(value.lstrip())] + html.escape(replacement, quote=False) + value[len(value.rstrip()):]
    chunks = re.split(r'(<[^>]+>)', source)
    for i, chunk in enumerate(chunks):
        if chunk.startswith('<'):
            chunks[i] = re.sub(r'(\b(?:alt|aria-label)\s*=\s*")([^"]*)(")',
                               lambda m: m[1] + html.escape(html.unescape(lookup(m[2])), quote=True) + m[3], chunk)
            if chunk.startswith('<meta') and 'name="description"' in chunk:
                chunks[i] = re.sub(r'(content=")([^"]*)(")',
                                   lambda m: m[1] + html.escape(html.unescape(lookup(m[2])), quote=True) + m[3], chunks[i])
        else:
            chunks[i] = lookup(chunk)
    return ''.join(chunks)


def language_switcher(lang, page):
    links = []
    for target in LANGUAGES:
        current = ' aria-current="true"' if lang == target else ''
        links.append(f'<a href="{route(target, page)}" lang="{target}" hreflang="{target}" aria-label="{NAMES[target]}"{current}>{target.upper()}</a>')
    return f'<div class="language-switcher" role="group" aria-label="{LABELS[lang]}">' + ''.join(links) + '</div>'


def generate(lang, page):
    source = (ROOT / f'site/templates/{page}.html').read_text()
    source = re.sub(r'\s*<!--.*?-->', '', source, flags=re.S)
    source = translate(source, lang, page)
    source = source.replace('<html lang="it">', f'<html lang="{lang}">')
    asset_prefix = 'assets/' if lang == 'en' else '../assets/'
    source = source.replace('"assets/', '"' + asset_prefix)
    source = source.replace('href="index.html', 'href="./')
    source = source.replace('href="index2.html"', 'href="./"')
    source = source.replace('</nav>', '</nav>\n      ' + language_switcher(lang, page), 1)
    source = source.replace('</head>', f'  <link rel="stylesheet" href="{asset_prefix}css/languages.css">\n</head>')
    subject, message = MESSAGES[lang]
    source = re.sub(r'href="mailto:[^"]+"', f'href="mailto:info@joia-pizzeria.com?subject={quote(subject)}"', source)
    source = re.sub(r'href="https://wa.me/[^"]+"', f'href="https://wa.me/34624633279?text={quote(message)}"', source)
    title = html.unescape(re.search(r'<title>(.*?)</title>', source)[1])
    description = html.unescape(re.search(r'<meta name="description" content="([^"]+)"', source)[1])
    url = ORIGIN + route(lang, page)
    metadata = [f'<link rel="canonical" href="{url}">']
    metadata += [f'<link rel="alternate" hreflang="{target}" href="{ORIGIN}{route(target, page)}">' for target in LANGUAGES]
    metadata.append(f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{route("en", page)}">')
    image = ORIGIN + '/assets/img/' + ('joia-terrazza.jpg' if page == 'home' else 'nduja-stracciatella.jpg')
    properties = {'og:type': 'website', 'og:site_name': 'JOIA', 'og:title': title, 'og:description': description,
                  'og:url': url, 'og:image': image, 'og:locale': {'en': 'en_GB', 'it': 'it_IT', 'es': 'es_ES'}[lang]}
    metadata += [f'<meta property="{key}" content="{html.escape(value, quote=True)}">' for key, value in properties.items()]
    metadata += [f'<meta property="og:locale:alternate" content="{locale}">' for target, locale in [('en', 'en_GB'), ('it', 'it_IT'), ('es', 'es_ES')] if target != lang]
    metadata += ['<meta name="twitter:card" content="summary_large_image">',
                 f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">',
                 f'<meta name="twitter:description" content="{html.escape(description, quote=True)}">',
                 f'<meta name="twitter:image" content="{image}">']
    structured = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title,
                  'description': description, 'url': url, 'inLanguage': lang,
                  'isPartOf': {'@type': 'WebSite', 'name': 'JOIA', 'url': ORIGIN + '/', 'inLanguage': list(LANGUAGES)}}
    metadata.append('<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c') + '</script>')
    source = source.replace('  <meta name="theme-color"', '  ' + '\n  '.join(metadata) + '\n  <meta name="theme-color"', 1)
    target = ROOT / route(lang, page).lstrip('/')
    if page == 'home':
        target = target / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source)


def sitemap():
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    xhtml = 'http://www.w3.org/1999/xhtml'
    ET.register_namespace('', ns)
    ET.register_namespace('xhtml', xhtml)
    root = ET.Element(f'{{{ns}}}urlset')
    for page in ('home', 'partner'):
        for lang in LANGUAGES:
            entry = ET.SubElement(root, f'{{{ns}}}url')
            ET.SubElement(entry, f'{{{ns}}}loc').text = ORIGIN + route(lang, page)
            for target in (*LANGUAGES, 'x-default'):
                ET.SubElement(entry, f'{{{xhtml}}}link', rel='alternate', hreflang=target,
                              href=ORIGIN + route('en' if target == 'x-default' else target, page))
    ET.indent(root)
    ET.ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /site/\nDisallow: /scripts/\n\nSitemap: {ORIGIN}/sitemap.xml\n')


if __name__ == '__main__':
    for page in ('home', 'partner'):
        for lang in LANGUAGES:
            generate(lang, page)
    sitemap()
    print('Generated 6 pages, sitemap.xml and robots.txt.')
