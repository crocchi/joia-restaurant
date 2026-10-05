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

## Existing content to review

The home presents **JOIA Pizza Bar**, while the existing partner page presents **JOIA Pasta Bar**. Their concepts have been preserved rather than rewritten. Both now use the home email `info@joia-pizzeria.com`. The partner footer still contains the original placeholder VAT ID (`00000000000`); replace it with the verified legal information before publishing.

Deployment and submission of the sitemap to Search Console are separate from this local implementation.
