# JOIA multilingual website

Static English (default), Italian and Spanish versions of the home and partner page.

| Language | Home | Partner |
| --- | --- | --- |
| English | `/` | `/partner.html` |
| Italian | `/it/` | `/it/partner.html` |
| Spanish | `/es/` | `/es/partner.html` |

## Updating the website

Edit the Italian source in `site/templates/home.html` or `site/templates/partner.html`.
Update the matching copy in `site/translations/en.json` and `site/translations/es.json`.
Brand slogans remain in English intentionally. The generator fails if new copy lacks a translation.

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

The generated HTML is committed alongside the sources and needs no runtime or package dependencies. Serve the project root with any static web server. Changes to generated pages will be overwritten by the next build.

## SEO and deployment

The production origin is configured in `site/config.json`: `https://www.joia-pizzeria.com`.
Each of the six pages has its own canonical, reciprocal `en`/`it`/`es` and `x-default` alternates, translated description, social metadata and WebPage structured data. English is the fallback. `sitemap.xml` contains all six canonical URLs, and `robots.txt` references it.

Upload the HTML pages, `it/`, `es/`, `assets/`, `robots.txt` and `sitemap.xml` together. The host must serve directory indexes (`/it/` → `/it/index.html`) and preserve `/partner.html` routes. Set the host to redirect HTTP and the non-www domain to the configured HTTPS www origin. If the host exposes `/index.html`, `/it/index.html` or `/es/index.html`, redirect these to their corresponding directory URLs where supported; canonicals already use directory URLs.

The unused original demo `index-other.html` is marked `noindex` and omitted from the sitemap. Source and script directories are excluded from crawling. Do not submit demo or source pages to Search Console.

## Restaurant information

All pages use the single brand **JOIA Pizzeria Contemporanea** (Callejón Gonzalo 2, 38650 Los Cristianos, Arona, Tenerife). The address and phone appear in the home contact section, and the home pages carry `Restaurant` structured data defined in `RESTAURANT` in `scripts/build_site.py`. Opening hours (Mon, Tue, Thu–Sat 13:00–22:00; Wed 17:00–22:00; Sun 13:00–23:00) appear in the home contact section and in `openingHoursSpecification`. The menu is hosted at https://menu.joia-pizzeria.com/ (redirects to caprimenu.com) and linked from the nav, the hero button and `hasMenu`. Legal entity: Joia Hospitality Group S.L. Contact email: `joiatenerife@hotmail.com`. Tax ID (NIF): B21895008.

Deployment and submission of the sitemap to Search Console are separate from this local implementation.
