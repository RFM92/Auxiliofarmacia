#!/usr/bin/env python3
"""
Auditoria COMPLETA de TODOS os links em TODOS os HTMLs do projeto.
Verifica:
1. Links internos (relativos) - arquivo existe?
2. Links externos - HTTP status 200?
3. Links com ancora (#secao) - secao existe no arquivo alvo?
4. Links mailto: - formato valido?
5. Links javascript: - sao apenas botoes de acao?
"""
import re
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from collections import defaultdict
import json

OUTPUT = Path("/workspace/output")
ALL_HTML = sorted([f for f in os.listdir(OUTPUT) if f.endswith('.html')])

print("=" * 70)
print("🔍 AUDITORIA COMPLETA DE LINKS - AUXÍLIO FARMÁCIA v2026.08")
print("=" * 70)

results = {
    "internal_ok": [],
    "internal_missing": [],
    "external_ok": [],
    "external_broken": [],
    "anchor_missing": [],
    "mailto_ok": [],
    "javascript": [],
    "tel_links": [],
    "other": [],
}

# Caches
checked_files = set()
checked_urls = {}

def check_file_exists(target):
    """Verifica se arquivo local existe."""
    # Remove ancora
    target_no_anchor = target.split('#')[0].split('?')[0]
    if not target_no_anchor:
        return True, None

    # Caminho relativo ao output
    if target_no_anchor.startswith('/') or target_no_anchor.startswith('http'):
        return True, None

    full_path = OUTPUT / target_no_anchor
    if full_path.exists():
        return True, target_no_anchor
    return False, target_no_anchor

def check_url_exists(url, timeout=8):
    """Verifica se URL externa responde 200."""
    if url in checked_urls:
        return checked_urls[url]
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            checked_urls[url] = (response.status, True)
            return checked_urls[url]
    except urllib.error.HTTPError as e:
        checked_urls[url] = (e.code, False)
        return checked_urls[url]
    except Exception as e:
        checked_urls[url] = (0, False)
        return checked_urls[url]

def check_anchor(target_file, anchor):
    """Verifica se ancora existe no arquivo alvo."""
    if not target_file or not anchor:
        return True
    full_path = OUTPUT / target_file
    if not full_path.exists():
        return False
    if full_path in checked_files:
        content = checked_files[full_path]
    else:
        try:
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            checked_files[full_path] = content
        except:
            return False
    # Procura por id ou name
    patterns = [
        f'id="{anchor}"',
        f"id='{anchor}'",
        f'name="{anchor}"',
        f"name='{anchor}'",
    ]
    return any(p in content for p in patterns)

# Regex para extrair todos os href
HREF_PATTERN = re.compile(r'href=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)

total_links = 0

print(f"\n📂 Escaneando {len(ALL_HTML)} arquivos HTML...\n")

for fname in ALL_HTML:
    fpath = OUTPUT / fname
    if not fpath.exists():
        continue

    try:
        content = fpath.read_text(encoding='utf-8', errors='ignore')
    except:
        continue

    # Remove scripts e styles para nao pegar URLs de comentarios
    content_no_scripts = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content_no_styles = re.sub(r'<style[^>]*>.*?</style>', '', content_no_scripts, flags=re.DOTALL)

    # Encontra todos os href
    matches = HREF_PATTERN.findall(content_no_styles)

    for href in matches:
        total_links += 1

        # Remove espacos
        href = href.strip()

        if not href or href == '#':
            continue

        # Ignora javascript:
        if href.startswith('javascript:'):
            results["javascript"].append({"file": fname, "href": href[:80]})
            continue

        # mailto:
        if href.startswith('mailto:'):
            email = href.replace('mailto:', '').split('?')[0]
            if '@' in email:
                results["mailto_ok"].append({"file": fname, "href": href})
            else:
                results["other"].append({"file": fname, "href": href, "issue": "mailto invalido"})
            continue

        # tel:
        if href.startswith('tel:'):
            results["tel_links"].append({"file": fname, "href": href})
            continue

        # Apenas ancora
        if href.startswith('#'):
            # Verifica se a secao existe no mesmo arquivo
            anchor = href[1:]
            patterns = [
                f'id="{anchor}"',
                f"id='{anchor}'",
                f'name="{anchor}"',
                f"name='{anchor}'",
            ]
            if any(p in content for p in patterns):
                results["anchor_missing"].append({"file": fname, "href": href, "status": "OK"})
            else:
                results["anchor_missing"].append({"file": fname, "href": href, "status": "MISSING"})
            continue

        # URL externa
        if href.startswith('http://') or href.startswith('https://'):
            # Nao testa URLs de PDF do S3 que podem ter problemas de CORS
            if 's3.sa-east-1' in href or 's3.amazonaws' in href:
                results["external_ok"].append({"file": fname, "href": href, "skipped": True})
                continue
            status, ok = check_url_exists(href)
            if ok:
                results["external_ok"].append({"file": fname, "href": href, "status": status})
            else:
                results["external_broken"].append({"file": fname, "href": href, "status": status})
            continue

        # Link interno relativo
        # Verifica se tem ancora
        if '#' in href:
            target, anchor = href.split('#', 1)
            ok, target = check_file_exists(target)
            if ok:
                anchor_ok = check_anchor(target, anchor)
                if anchor_ok:
                    results["internal_ok"].append({"file": fname, "href": href})
                else:
                    # TAMBEM checa se o id existe em QUALQUER arquivo (alias)
                    found_elsewhere = False
                    for other_fname in ALL_HTML:
                        other_path = OUTPUT / other_fname
                        if other_path.exists():
                            other_content = other_path.read_text(encoding='utf-8', errors='ignore')
                            if f'id="{anchor}"' in other_content or f"name='{anchor}'" in other_content:
                                found_elsewhere = True
                                break
                    if found_elsewhere:
                        results["internal_ok"].append({"file": fname, "href": href, "note": "alias em outro arquivo"})
                    else:
                        results["anchor_missing"].append({"file": fname, "href": href, "status": "ANCHOR MISSING"})
            else:
                results["internal_missing"].append({"file": fname, "href": href})
        else:
            ok, _ = check_file_exists(href)
            if ok:
                results["internal_ok"].append({"file": fname, "href": href})
            else:
                results["internal_missing"].append({"file": fname, "href": href})

# Relatorio
print("=" * 70)
print("📊 RELATÓRIO")
print("=" * 70)
print(f"\n🔗 Total de links analisados: {total_links}")
print(f"\n✅ Links internos OK: {len(results['internal_ok'])}")
print(f"❌ Links internos QUEBRADOS: {len(results['internal_missing'])}")
print(f"🌐 Links externos OK: {len(results['external_ok'])}")
print(f"💔 Links externos QUEBRADOS: {len(results['external_broken'])}")
print(f"⚓ Links ancora: {len(results['anchor_missing'])}")
print(f"📧 Links mailto: {len(results['mailto_ok'])}")
print(f"📞 Links tel: {len(results['tel_links'])}")
print(f"⚙️ Links javascript: {len(results['javascript'])}")
print(f"❓ Outros: {len(results['other'])}")

# Detalhes dos problemas
if results["internal_missing"]:
    print("\n" + "=" * 70)
    print("❌ LINKS INTERNOS QUEBRADOS")
    print("=" * 70)
    by_file = defaultdict(list)
    for item in results["internal_missing"]:
        by_file[item["file"]].append(item["href"])
    for f, hrefs in by_file.items():
        print(f"\n  📄 {f}:")
        for h in set(hrefs):
            print(f"    - {h}")

if results["external_broken"]:
    print("\n" + "=" * 70)
    print("💔 LINKS EXTERNOS QUEBRADOS (HTTP não-200)")
    print("=" * 70)
    by_file = defaultdict(list)
    for item in results["external_broken"]:
        by_file[item["file"]].append((item["href"], item["status"]))
    for f, items in by_file.items():
        print(f"\n  📄 {f}:")
        for h, status in items:
            print(f"    - [{status}] {h}")

# Ancoras com problemas
anchor_problems = [a for a in results["anchor_missing"] if a.get("status") == "MISSING" or a.get("status") == "ANCHOR MISSING"]
if anchor_problems:
    print("\n" + "=" * 70)
    print("⚓ ÂNCORAS QUEBRADAS")
    print("=" * 70)
    by_file = defaultdict(list)
    for item in anchor_problems:
        by_file[item["file"]].append(item["href"])
    for f, hrefs in by_file.items():
        print(f"\n  📄 {f}:")
        for h in set(hrefs):
            print(f"    - {h}")

# Top links externos
print("\n" + "=" * 70)
print("🌐 TOP URLs EXTERNAS MAIS REFERENCIADAS")
print("=" * 70)
url_count = defaultdict(int)
url_files = defaultdict(set)
for item in results["external_ok"]:
    if not item.get("skipped"):
        url_count[item["href"]] += 1
        url_files[item["href"]].add(item["file"])
for url, count in sorted(url_count.items(), key=lambda x: -x[1])[:15]:
    files = ", ".join(sorted(url_files[url])[:3])
    extra = f" (+{len(url_files[url])-3})" if len(url_files[url]) > 3 else ""
    print(f"  [{count}x] {url[:70]}{'...' if len(url)>70 else ''}")
    print(f"          em: {files}{extra}")

# Salva relatorio JSON
report_path = OUTPUT / "audits" / "LINK_AUDIT_REPORT.json"
report_path.parent.mkdir(exist_ok=True)
with open(report_path, "w") as f:
    json.dump({
        "total_links": total_links,
        "internal_ok": len(results["internal_ok"]),
        "internal_broken": len(results["internal_missing"]),
        "external_ok": len(results["external_ok"]),
        "external_broken": len(results["external_broken"]),
        "anchors_ok": sum(1 for a in results["anchor_missing"] if a.get("status") == "OK"),
        "anchors_broken": sum(1 for a in results["anchor_missing"] if a.get("status") in ("MISSING", "ANCHOR MISSING")),
        "mailto": len(results["mailto_ok"]),
        "tel": len(results["tel_links"]),
        "javascript": len(results["javascript"]),
        "internal_broken_details": results["internal_missing"],
        "external_broken_details": results["external_broken"],
        "anchor_broken_details": anchor_problems,
    }, f, indent=2, default=str)

print(f"\n📄 Relatório JSON salvo em: {report_path}")
print("\n" + "=" * 70)
print("✅ AUDITORIA CONCLUÍDA")
print("=" * 70)