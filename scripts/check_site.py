#!/usr/bin/env python3
"""Check indexable pages, local links, language alternates and sitemap consistency."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = json.loads((ROOT / 'site/config.json').read_text())['origin']
PAGES = ['index.html', 'partner.html', 'it/index.html', 'it/partner.html', 'es/index.html', 'es/partner.html']

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.nodes = []
        self.ids = set()
        self.jsonld = []
        self.in_json = False
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.nodes.append((tag, attrs))
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, (self.path, 'Duplicate ID', attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_json = True
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_json = False
    def handle_data(self, data):
        if self.in_json:
            self.jsonld.append(json.loads(data))

pages = {name: Page(ROOT / name) for name in PAGES}
for name, page in pages.items():
    lang = name.split('/')[0] if '/' in name else 'en'
    assert next(a['lang'] for t,a in page.nodes if t == 'html') == lang
    assert len([1 for t,a in page.nodes if t == 'h1']) == 1
    assert len([1 for t,a in page.nodes if t == 'meta' and a.get('name') == 'description']) == 1
    canonical = [a['href'] for t,a in page.nodes if t == 'link' and a.get('rel') == 'canonical']
    expected = ORIGIN + '/' + (name.removesuffix('index.html') if name.endswith('index.html') else name)
    assert canonical == [expected], (name, canonical, expected)
    alternates = {a['hreflang']: a['href'] for t,a in page.nodes if t == 'link' and a.get('rel') == 'alternate'}
    assert set(alternates) == {'en', 'it', 'es', 'x-default'}
    assert alternates[lang] == expected and alternates['x-default'] == alternates['en']
    partner = name.endswith('partner.html')
    for target in ('en', 'it', 'es'):
        suffix = ('' if target == 'en' else target + '/') + ('partner.html' if partner else '')
        assert alternates[target] == ORIGIN + '/' + suffix
    selectors = [a for t,a in page.nodes if t == 'a' and a.get('hreflang')]
    assert len(selectors) == 3 and len([a for a in selectors if a.get('aria-current') == 'true']) == 1
    assert page.jsonld[0]['inLanguage'] == lang and page.jsonld[0]['url'] == expected
    for tag, attrs in page.nodes:
        for attr in ('href','src'):
            if attr not in attrs:
                continue
            parsed = urlsplit(attrs[attr])
            if parsed.scheme or parsed.netloc:
                continue
            if not parsed.path:
                target = page.path
            else:
                target = (ROOT / parsed.path.lstrip('/')) if parsed.path.startswith('/') else page.path.parent / unquote(parsed.path)
                if target.is_dir():
                    target = target / 'index.html'
            assert target.exists(), (name, attrs[attr], 'Missing target')
            if parsed.fragment:
                assert parsed.fragment in Page(target).ids, (name, attrs[attr], 'Missing anchor')
        if tag == 'img':
            assert attrs.get('alt'), (name, 'Missing image alt')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
entries = ET.parse(ROOT / 'sitemap.xml').findall('s:url', ns)
assert len(entries) == 6
assert {e.find('s:loc', ns).text for e in entries} == {next(a['href'] for t,a in p.nodes if t == 'link' and a.get('rel')=='canonical') for p in pages.values()}
for entry in entries:
    assert len(entry.findall('x:link', ns)) == 4
assert f'Sitemap: {ORIGIN}/sitemap.xml' in (ROOT / 'robots.txt').read_text()
print('PASS: 6 pages, canonical URLs, reciprocal language alternates, structured data, sitemap, assets and local anchors.')
